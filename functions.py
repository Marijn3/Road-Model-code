import geopandas as gpd
import pandas as pd
from shapely import *
import csv
from copy import deepcopy
import math

pd.set_option('display.max_columns', None)
GRID_SIZE = 0.00001
MSI_RELATION_MAX_SEARCH_DISTANCE = 5000


class DataFrameLoader:
    """
   A class for loading GeoDataFrames from shapefiles based on a specified location extent.

   Attributes:
       __LOCATIONS_CSV_PATH (str): The file path for the locations csv file.
       __FILE_PATHS (list): List of file paths for shapefiles to be loaded.
       data (dict): Dictionary to store GeoDataFrames for each layer.
       extent (box): The extent of the specified location.
   """

    __LOCATIONS_CSV_PATH = 'data/locaties.csv'

    # List all data layer files to be loaded. Same structure as WEGGEG.
    __FILE_PATHS = [
        "data/Wegcat beleving/wegcat_beleving-edit.dbf",
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        "data/Mengstroken/mengstroken.dbf",
        "data/Maximum snelheid/max_snelheden.dbf",
        "data/Convergenties/convergenties.dbf",
        "data/Divergenties/divergenties.dbf",
        "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    def __init__(self, location: str = None) -> None:
        self.data = {}
        self.extent = None
        if location:
            self.__load_dataframes(location)

    def __load_dataframes(self, location: str) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            location (str): The name of the location.
        """
        self.__define_extent(location)
        for file_path in DataFrameLoader.__FILE_PATHS:
            df_layer_name = self.__get_layer_name(file_path)
            self.data[df_layer_name] = self.__load_dataframe(file_path)
            self.__edit_columns(df_layer_name)

    def __load_dataframe(self, file_path: str) -> gpd.GeoDataFrame:
        """
        Load the extent-intersecting parts of a GeoDataFrame from a shapefile.
        Args:
            file_path (str): The path to the shapefile.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with selected data.
        """
        data = gpd.read_file(file_path)
        return self.__select_data_in_extent(data)

    def __define_extent(self, location: str) -> None:
        """
        Determine the extent box of the specified location from coordinates.
        Stores it in self.extent.
        Args:
            location (str): The name of the location.
        Raises:
            ValueError: If the specified location is not found in the csv file.
        """
        coords = self.__load_extent_from_csv(location)

        if coords:
            self.extent = box(xmin=coords["west"], ymin=coords["south"], xmax=coords["east"], ymax=coords["north"])
        else:
            raise ValueError(f"Ongeldige locatie: {location}. Voer een geldige naam van een locatie in.")

    def __select_data_in_extent(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Select data that intersects the specified extent from the GeoDataFrame.
        All data that intersects the extent is considered 'in the extent'.
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with only data that intersects the extent.
        """
        data['inextent'] = data['geometry'].apply(lambda geom: geom.intersects(self.extent))
        return data[data['inextent']]

    @staticmethod
    def __get_layer_name(file_path) -> str:
        """
        Extract the layer name from the file path.
        Works well with the file paths in the original WEGGEG files.
        Args:
            file_path (str): The path to the file.
        Returns:
            str: The layer name.
        """
        # Folder name is extracted and used as the layer name.
        parts = file_path.split("/")
        folder_name = parts[-2]
        return folder_name

    @staticmethod
    def convert_to_linestring(geom: MultiLineString) -> LineString:
        merged = line_merge(geom)
        if isinstance(merged, LineString):
            return merged

        # Catching a specific case where there is a slight mismatch in the endpoints of a multilinestring
        if get_num_geometries(geom) == 2:
            line1 = geom.geoms[0]
            line1_points = [line1.coords[0], line1.coords[1], line1.coords[-2], line1.coords[-1]]

            line2 = geom.geoms[1]
            line2_points = [line2.coords[0], line2.coords[1], line2.coords[-2], line2.coords[-1]]

            common_points = [point for point in line1_points if point in line2_points]
            assert len(common_points) == 1, f"Meer dan één punt gemeen tussen {line1} en {line2}: {common_points}"
            common_point = common_points[0]
            index_line1 = line1_points.index(common_point)
            index_line2 = line2_points.index(common_point)

            if index_line1 == 1:
                line1 = LineString([coord for coord in line1.coords if coord != line1_points[0]])
            if index_line1 == 2:
                line1 = LineString([coord for coord in line1.coords if coord != line1_points[-1]])
            if index_line2 == 1:
                line2 = LineString([coord for coord in line2.coords if coord != line2_points[0]])
            if index_line2 == 2:
                line2 = LineString([coord for coord in line2.coords if coord != line2_points[-1]])

            return line_merge(MultiLineString([line1, line2]))

        assert False, f"Omzetting naar LineString mislukt voor {geom}"

    def __edit_columns(self, name: str) -> None:
        """
        Edits columns of GeoDataFrames in self.data in place.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        # Ensure all MultiLineStrings are converted to LineStrings.
        self.data[name]['geometry'] = self.data[name]['geometry'].apply(lambda geom: self.convert_to_linestring(geom)
                                                                        if isinstance(geom, MultiLineString) else geom)

        # These column variable types should be changed.
        self.data[name]['WEGNUMMER'] = pd.to_numeric(self.data[name]['WEGNUMMER'], errors='coerce').astype('Int64')

        # Mapping from lane registration to (nLanes, Special feature)
        lane_mapping_h = {'1 -> 1': (1, None), '1 -> 2': (2, 'ExtraRijstrook'), '2 -> 1': (2, 'Rijstrookbeëindiging'),
                          '1 -> 1.6': (1, 'TaperStart'), '1.6 -> 1': (1, 'TaperEinde'),
                          '2 -> 1.6': (2, 'TaperStart'), '1.6 -> 2': (2, 'TaperEinde'),
                          '2 -> 2': (2, None), '2 -> 3': (3, 'ExtraRijstrook'), '3 -> 2': (3, 'Rijstrookbeëindiging'),
                          '3 -> 3': (3, None), '3 -> 4': (4, 'ExtraRijstrook'), '4 -> 3': (4, 'Rijstrookbeëindiging'),
                          '4 -> 4': (4, None), '4 -> 5': (5, 'ExtraRijstrook'), '5 -> 4': (5, 'Rijstrookbeëindiging'),
                          '5 -> 5': (5, None), '5 -> 6': (6, 'ExtraRijstrook'), '6 -> 5': (6, 'Rijstrookbeëindiging'),
                          '6 -> 6': (6, None),
                          '7 -> 7': (7, None)}
        # All registrations with T as kantcode as marked in the opposite direction.
        lane_mapping_t = {'1 -> 1': (1, None), '1 -> 2': (2, 'Rijstrookbeëindiging'), '2 -> 1': (2, 'ExtraRijstrook'),
                          '1 -> 1.6': (1, 'TaperEinde'), '1.6 -> 1': (1, 'TaperStart'),
                          '2 -> 1.6': (2, 'TaperEinde'), '1.6 -> 2': (2, 'TaperStart'),
                          '2 -> 2': (2, None), '2 -> 3': (3, 'Rijstrookbeëindiging'), '3 -> 2': (3, 'ExtraRijstrook'),
                          '3 -> 3': (3, None), '3 -> 4': (4, 'Rijstrookbeëindiging'), '4 -> 3': (4, 'ExtraRijstrook'),
                          '4 -> 4': (4, None), '4 -> 5': (5, 'Rijstrookbeëindiging'), '5 -> 4': (5, 'ExtraRijstrook'),
                          '5 -> 5': (5, None), '5 -> 6': (6, 'Rijstrookbeëindiging'), '6 -> 5': (6, 'ExtraRijstrook'),
                          '6 -> 6': (6, None),
                          '7 -> 7': (7, None)}

        if name == 'Rijstroken':
            self.data[name]['VOLGNRSTRK'] = pd.to_numeric(self.data[name]['VOLGNRSTRK'], errors='coerce').astype('Int64')

            mapping_function = lambda row: lane_mapping_h.get(row['OMSCHR'], row['OMSCHR']) \
                if row['KANTCODE'] == "H" \
                else lane_mapping_t.get(row['OMSCHR'], row['OMSCHR'])
            self.data[name]['laneInfo'] = self.data[name].apply(mapping_function, axis=1)

        if name == 'Mengstroken':
            mapping_function = lambda row: lane_mapping_h.get(row['AANT_MSK'], row['AANT_MSK']) \
                if row['KANTCODE'] == "H" \
                else lane_mapping_t.get(row['AANT_MSK'], row['AANT_MSK'])
            self.data[name]['laneInfo'] = self.data[name].apply(mapping_function, axis=1)

        if name == 'Kantstroken':
            # 'Redresseerstrook', 'Bufferstrook', 'Pechhaven' and such are not considered
            is_considered = self.data[name]['OMSCHR'].isin(['Vluchtstrook', 'Puntstuk', 'Spitsstrook', 'Plusstrook'])
            self.data[name] = self.data[name][is_considered]

        if name == 'Rijstrooksignaleringen':
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            is_kp = self.data[name]['CODE'] == 'KP'
            self.data[name] = self.data[name][is_kp]

        if 'stroken' in name:
            # All 'stroken' dataframes have VNRWOL columns which should be converted to integer.
            self.data[name]['VNRWOL'] = pd.to_numeric(self.data[name]['VNRWOL'], errors='coerce').astype('Int64')

    @staticmethod
    def __load_extent_from_csv(location: str) -> dict[str, float]:
        """
        Load the extent coordinates of the specified location from the csv file.
        Args:
            location (str): The name of the location.
        Returns:
            dict: The extent coordinates (north, east, south, west).
        Raises:
            FileNotFoundError: If the file in the location of the filepath is not found.
            ValueError: If there is an error reading the csv file.
        """
        try:
            with open(DataFrameLoader.__LOCATIONS_CSV_PATH, 'r') as file:
                csv_reader = csv.DictReader(file, delimiter=';')
                for row in csv_reader:
                    if row['locatie'] == location:
                        return {
                            'north': float(row['noord']),
                            'east': float(row['oost']),
                            'south': float(row['zuid']),
                            'west': float(row['west']),
                        }
            return {}  # Return empty dictionary if the location is not found
        except FileNotFoundError:
            raise FileNotFoundError(f"Bestand niet gevonden: {DataFrameLoader.__LOCATIONS_CSV_PATH}")
        except csv.Error as e:
            raise ValueError(f"Fout bij het lezen van het csv bestand: {e}")


class RoadModel:
    __LAYER_NAMES = ['Wegcat beleving', 'Rijstroken', 'Kantstroken', 'Mengstroken', 'Maximum snelheid',
                     'Rijstrooksignaleringen', 'Convergenties', 'Divergenties']

    def __init__(self, dfl: DataFrameLoader):
        self.sections = {}
        self.section_index = 0
        self.points = {}
        self.point_index = 0
        self.has_initial_layer = False

        self.__import_dataframes(dfl)

    def __import_dataframes(self, dfl: DataFrameLoader) -> None:
        """
        Load road attributes from all DataFrames.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
        Note:
            The 'Wegcat beleving' layer is the first layer to be imported because two assumptions hold for it:
                1) it is defined everywhere where it would be necessary.
                2) it does not have internal overlap.
                3) Additionally, it is a reliable source for roadside/rijrichting.
        """
        for df_name in self.__LAYER_NAMES:
            print(f"[STATUS:] Laag '{df_name}' wordt geïmporteerd...")
            current_sections = self.section_index
            current_points = self.point_index

            self.__import_dataframe(dfl, df_name)

            print(f"[STATUS:] {df_name} voegde {self.section_index - current_sections} secties "
                  f"en {self.point_index - current_points} punten toe aan het model.\n"
                  f"Het model heeft nu in totaal {self.section_index} secties en {self.point_index} punten.\n")

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str):
        """
        Load line and point features and their attributes from a GeoDataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of DataFrame to be imported.
        """
        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            feature_info = self.__extract_row_properties(row, df_name)

            if not self.has_initial_layer:
                self.__add_section(feature_info)
                continue

            if isinstance(row['geometry'], (Point, MultiPoint)):
                self.__add_point(feature_info)
            else:
                self.__determine_sectioning(feature_info)

        self.has_initial_layer = True

    def __extract_row_properties(self, row: pd.Series, name: str):
        """
        Turns the contents of a GeoDataframe row into a dictionary with the relevant entries.
        Args:
            row (pd.Series): Row containing information about the road section
            name (str): Name of dataframe.
        """
        if isinstance(row['geometry'], (Point, MultiPoint)):
            return self.__extract_point_properties(row, name)
        else:
            return self.__extract_line_properties(row, name)

    def __extract_point_properties(self, row: pd.Series, name: str):
        properties = {}

        # TODO: This part should be moved to DFL class.
        VERGENCE_TYPE_MAPPING = {
            'U': 'Uitvoeging',
            'D': 'Splitsing',
            'C': 'Samenvoeging',
            'I': 'Invoeging'
        }

        km = row['KMTR']
        geometrie = row['geometry']

        overlapping_sections = self.get_sections_at_point(geometrie)

        # Get the roadside letter and number from the (first) section it overlaps
        rijrichting = [section_info['Rijrichting'] for section_info in overlapping_sections.values()][0]
        wegnummer = [section_info['Wegnummer'] for section_info in overlapping_sections.values()][0]

        # Get the IDs of the sections it overlaps
        section_ids = [section_id for section_id in overlapping_sections.keys()]

        # Get the local number of (main) lanes. Take the highest value if there are multiple.
        lane_info = [self.get_n_lanes(section_info['Eigenschappen']) for section_info in overlapping_sections.values()]
        properties['Aantal_Hoofdstroken'] = max(lane_info, key=lambda x: x[0])[0]
        properties['Aantal_Stroken'] = max(lane_info, key=lambda x: x[1])[1]

        # Get the local orientation
        properties['Lokale_hoek'] = self.get_local_angle(section_ids, geometrie)

        if name == 'Convergenties':
            properties['Type'] = VERGENCE_TYPE_MAPPING.get(row['TYPE_CONV'], "Unknown")
            properties['Ingaande_Secties'] = [section_id for section_id, section_info in overlapping_sections.items()
                                      if self.get_n_lanes(section_info['Eigenschappen'])[1] != properties['Aantal_Stroken']]
            properties['Uitgaande_Secties'] = [section_id for section_id, section_info in overlapping_sections.items()
                                      if self.get_n_lanes(section_info['Eigenschappen'])[1] == properties['Aantal_Stroken']]

        if name == 'Divergenties':
            properties['Type'] = VERGENCE_TYPE_MAPPING.get(row['TYPE_DIV'], "Unknown")
            properties['Ingaande_Secties'] = [section_id for section_id, section_info in overlapping_sections.items()
                                      if self.get_n_lanes(section_info['Eigenschappen'])[1] == properties['Aantal_Stroken']]
            properties['Uitgaande_Secties'] = [section_id for section_id, section_info in overlapping_sections.items()
                                      if self.get_n_lanes(section_info['Eigenschappen'])[1] != properties['Aantal_Stroken']]

        if name == 'Rijstrooksignaleringen':
            properties['Type'] = 'Signalering'
            properties['Rijstroken'] = [int(char) for char in row['RIJSTRKNRS']]

        return {'Rijrichting': rijrichting,
                'Wegnummer': wegnummer,
                'km': km,
                'section_ids': section_ids,
                'Eigenschappen': properties,
                'Geometrie': geometrie}

    @staticmethod
    def __extract_line_properties(row: pd.Series, name: str):
        rijrichting = None
        wegnummer = None
        km_bereik = [row['BEGINKM'], row['EINDKM']]
        properties = {}

        geom = set_precision(row['geometry'], GRID_SIZE)
        # if isinstance(geom, MultiLineString):
        #     geom = line_merge(geom)

        if name == "Wegcat beleving":
            if row['OMSCHR'] == 'Autosnelweg':
                wegletter = 'A'  # Autosnelweg
            else:
                wegletter = 'N'  # Niet-autosnelweg

            rijrichting = row['IZI_SIDE']
            wegnummer = wegletter + str(row['WEGNUMMER'])

            # Flip range only if rijrichting is L.
            if rijrichting == 'L':
                km_bereik = [row['EINDKM'], row['BEGINKM']]

        elif name == 'Rijstroken':
            first_lane_number = row['VNRWOL']
            n_lanes, special = row['laneInfo']

            # Indicate lane number and type of lane. Example: {1: 'Rijstrook', 2: 'Rijstrook'}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                properties[lane_nr] = 'Rijstrook'

            # Take note of special circumstances on this feature.
            if special:
                changing_lane = row['VOLGNRSTRK']
                properties['Special'] = (special, changing_lane)

        elif name == 'Kantstroken':
            # Indicate lane number and type of kantstrook. Example: {3: 'Spitsstrook'}
            lane_number = row['VNRWOL']
            properties[lane_number] = row['OMSCHR']

        elif name == 'Mengstroken':
            first_lane_number = row['VNRWOL']
            n_lanes, special = row['laneInfo']

            # Indicate lane number and type of lane. Example: {4: 'Weefstrook'}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                properties[lane_nr] = row['OMSCHR']

            # Take note of special circumstances on this feature.
            if special:
                properties['Special'] = special

        elif name == 'Maximum snelheid':
            properties['Maximumsnelheid'] = row['OMSCHR']

        return {'Rijrichting': rijrichting,
                'Wegnummer': wegnummer,
                'Km_bereik': km_bereik,
                'Eigenschappen': properties,
                'Geometrie': geom}

    def __determine_sectioning(self, new_section: dict) -> None:
        """
        Merges the given section with existing sections in self.sections.
        Args:
            new_section (dict): Information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            print(f"[WAARSCHUWING:] {new_section} overlapt niet met eerdere lagen. Deze sectie wordt niet toegevoegd.")
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            return

        overlap_section = overlap_sections.pop(0)

        other_section_index = overlap_section['index']
        overlap_section_info = deepcopy(overlap_section['section_info'])

        other_section_side = overlap_section_info['Rijrichting']
        other_section_wegnummer = overlap_section_info['Wegnummer']
        other_section_range = overlap_section_info['Km_bereik']
        other_section_props = overlap_section_info['Eigenschappen']
        other_section_geom = overlap_section_info['Geometrie']

        new_section_range = new_section['Km_bereik']

        # Align new section range according to existing sections
        if other_section_side == 'L':
            new_section_range.reverse()

        new_section_props = new_section['Eigenschappen']

        # Ensure all new geometries are also oriented in driving direction
        if same_direction(other_section_geom, new_section['Geometrie']):
            new_section_geom = new_section['Geometrie']
        else:
            new_section_geom = reverse(new_section['Geometrie'])

        sections_to_remove = set()

        while True:

            if not get_overlap(new_section_geom, other_section_geom):
                overlap_section = overlap_sections.pop(0)

                other_section_index = overlap_section['index']
                overlap_section_info = deepcopy(overlap_section['section_info'])

                other_section_range = overlap_section_info['Km_bereik']
                other_section_props = overlap_section_info['Eigenschappen']
                other_section_geom = overlap_section_info['Geometrie']

            # print("New section range:", new_section_range)
            # print("New section props:", new_section_props)
            # print("New section geom:", set_precision(new_section['Geometrie'], 1))
            # print("Other section range:", other_section_range)
            # print("Other section props:", other_section_props)
            # print("Other section geom:", set_precision(other_section_geom, 1))

            assert determine_range_overlap(new_section_range, other_section_range), "Bereiken overlappen niet."
            if abs(get_km_length(new_section['Km_bereik']) - new_section['Geometrie'].length) > 100:
                print(
                    f"[WAARSCHUWING:] Groot lengteverschil: {get_km_length(new_section['Km_bereik'])} en {new_section['Geometrie'].length}\n")

            # TODO: Fancier implementation making use of the symmetry of the code below.

            right_side = other_section_side == 'R'
            left_side = other_section_side == 'L'

            new_section_first = (
                                    (min(new_section_range) < min(other_section_range) and right_side)
                                ) or (
                                    (max(new_section_range) > max(other_section_range) and left_side))

            both_sections_first = (
                                      (min(new_section_range) == min(other_section_range) and right_side)
                                  ) or (
                                      (max(new_section_range) == max(other_section_range) and left_side))

            other_section_first = (
                                      (min(new_section_range) > min(other_section_range) and right_side)
                                  ) or (
                                      (max(new_section_range) < max(other_section_range) and left_side))

            # Case A: new_section starts earlier.
            # Add section between new_section_start and other_section_start
            # with new_section properties and geometry
            if new_section_first:
                # Add section...
                if right_side:
                    km_bereik = [min(new_section_range), min(other_section_range)]
                else:
                    km_bereik = [max(new_section_range), max(other_section_range)]
                added_geom = get_first_remainder(new_section_geom, other_section_geom)
                self.__add_section({
                    'Rijrichting': other_section_side,
                    'Wegnummer': other_section_wegnummer,
                    'Km_bereik': km_bereik,
                    'Eigenschappen': new_section_props,
                    'Geometrie': added_geom
                })
                # Trim the new_section range and geometry for next iteration.
                if right_side:
                    new_section_range = [min(other_section_range), max(new_section_range)]
                else:
                    new_section_range = [max(other_section_range), min(new_section_range)]
                new_section_geom = get_first_remainder(new_section_geom, added_geom)

            # Case B: start is equal.
            elif both_sections_first:

                other_ends_equal = (
                                       (max(new_section_range) == max(other_section_range) and right_side)
                                   ) or (
                                       (min(new_section_range) == min(other_section_range) and left_side))

                other_section_larger = (
                                           (max(new_section_range) < max(other_section_range) and right_side)
                                       ) or (
                                           (min(new_section_range) > min(other_section_range) and left_side))

                new_section_larger = (
                                         (max(new_section_range) > max(other_section_range) and right_side)
                                     ) or (
                                         (min(new_section_range) < min(other_section_range) and left_side))

                # Update the overlapping section properties
                if other_ends_equal:
                    if not (equals(new_section_geom, other_section_geom) or (
                            equals_exact(new_section_geom, other_section_geom, tolerance=0.1))):
                        print(f"[WAARSCHUWING:] Geometrieën komen niet helemaal overeen: "
                              f"{new_section_geom} and {other_section_geom}\n")
                    self.__update_section(other_section_index,
                                          km_bereik=new_section_range,
                                          eig=new_section_props,
                                          geometrie=other_section_geom)
                    # This is the final iteration.
                    break

                # Add section between new_section_min and new_section_max
                # with both properties and overlapping geometry.
                # Update other_section range between new_section_max and other_section_max
                # with and remaining geometry.
                # Remove old other_section.
                elif other_section_larger:
                    if right_side:
                        km_bereik = [min(new_section_range), max(new_section_range)]
                    else:
                        km_bereik = [max(new_section_range), min(new_section_range)]

                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    assert added_geom, f"Geen overlap gevonden tussen {new_section_geom} en {other_section_geom}."
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'Rijrichting': other_section_side,
                        'Wegnummer': other_section_wegnummer,
                        'Km_bereik': km_bereik,
                        'Eigenschappen': both_props,
                        'Geometrie': added_geom
                    })
                    if right_side:
                        km_remaining = [max(new_section_range), max(other_section_range)]
                    else:
                        km_remaining = [min(new_section_range), min(other_section_range)]
                    other_geom = get_first_remainder(other_section_geom, added_geom)
                    self.__update_section(other_section_index,
                                          km_bereik=km_remaining,
                                          geometrie=other_geom)
                    # This is the final iteration.
                    break

                elif new_section_larger:
                    # Add section with both properties
                    if right_side:
                        km_bereik = [min(new_section_range), max(other_section_range)]
                    else:
                        km_bereik = [max(new_section_range), min(other_section_range)]
                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'Rijrichting': other_section_side,
                        'Wegnummer': other_section_wegnummer,
                        'Km_bereik': km_bereik,
                        'Eigenschappen': both_props,
                        'Geometrie': added_geom
                    })
                    # We can remove the old other_section from the road model, since it has now been completely used.
                    sections_to_remove.add(other_section_index)
                    # Trim the new_section range and geometry for another iteration.
                    if right_side:
                        new_section_range = [max(other_section_range), max(new_section_range)]
                    else:
                        new_section_range = [min(other_section_range), min(new_section_range)]
                    new_section_geom = get_first_remainder(new_section_geom, added_geom)
                    # Determine if there are more overlapping sections to deal with.
                    if overlap_sections:
                        continue
                    else:
                        # This is the final iteration
                        self.__add_section({
                            'Rijrichting': other_section_side,
                            'Wegnummer': other_section_wegnummer,
                            'Km_bereik': new_section_range,
                            'Eigenschappen': new_section_props,
                            'Geometrie': new_section_geom
                        })
                        break

                else:
                    raise Exception("Er is iets misgegaan met het bereik.")

            # Case C: new_section starts later.
            # Add section between other_section_start and new_section_start
            # with other_section properties and geometry.
            elif other_section_first:
                # Add section...
                if right_side:
                    km_bereik = [min(other_section_range), min(new_section_range)]
                else:
                    km_bereik = [max(other_section_range), max(new_section_range)]
                added_geom = get_first_remainder(other_section_geom, new_section_geom)
                self.__add_section({
                    'Rijrichting': other_section_side,
                    'Wegnummer': other_section_wegnummer,
                    'Km_bereik': km_bereik,
                    'Eigenschappen': other_section_props,
                    'Geometrie': added_geom
                })
                # Trim the other_section range and geometry for next iteration.
                if right_side:
                    other_section_range = [min(new_section_range), max(other_section_range)]
                else:
                    other_section_range = [max(new_section_range), min(other_section_range)]
                other_section_geom = get_first_remainder(other_section_geom, added_geom)

            else:
                raise Exception("Er is iets misgegaan met het bereik.")

        self.__remove_sections(sections_to_remove)

    def __remove_sections(self, indices: set[int]) -> None:
        """
        Removes sections at the given indices.
        Args:
            indices (set): Set of indices at which to remove sections.
        """
        for index in indices:
            self.sections.pop(index)
            print(f"[LOG:] Sectie {index} verwijderd.\n")

    def __update_section(self, index: int, km_bereik: list = None, eig: dict = None, geometrie: LineString = None) -> None:
        """
        Updates one or more properties of a section at a given index.
        Prints log of section update.
        Args:
            index (int): Index of section to be updated
            km_bereik (list[float]): Start and end registration kilometre.
            eig (dict): All properties that belong to the section.
            geometrie (LineString): The geometry of the section.
        Prints:
            Changed section properties.
        """
        assert any([km_bereik, eig, geometrie]), "Update section aangeroepen, maar er is geen update nodig."
        assert km_bereik and geometrie or not (km_bereik or geometrie), \
            "Als de geometrie wordt aangepast, moet ook het bereik worden bijgewerkt. Dit geldt ook andersom."

        if km_bereik:
            if abs(get_km_length(km_bereik) - geometrie.length) > 100:
                print(f"[WAARSCHUWING:] Groot lengteverschil: {get_km_length(km_bereik)} en {geometrie.length}\n")
            self.sections[index]['Km_bereik'] = km_bereik
        if eig:
            self.sections[index]['Eigenschappen'].update(eig)
        if geometrie:
            self.sections[index]['Geometrie'] = geometrie

        self.__log_section_change(index)

    def __add_section(self, new_section: dict) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict): Containing:
                - Rijrichting (str): Side of the road. Either 'R' or 'L'.
                - Wegnummer (str): Letter and number indicating the name of the road.
                - Km_bereik (list[float]): Start and end registration kilometre.
                - Eigenschappen (dict): All properties that belong to the section.
                - Geometrie (LineString): The geometry of the section.
        Prints:
            Newly added section properties.
        """
        assert not is_empty(new_section['Geometrie']), f"Poging om een lege lijngeometrie toe te voegen: {new_section}"
        if abs(get_km_length(new_section['Km_bereik']) - new_section['Geometrie'].length) > 100:
            print(f"[WAARSCHUWING:] Groot lengteverschil: "
                  f"{get_km_length(new_section['Km_bereik'])} en {new_section['Geometrie'].length}\n")

        self.sections[self.section_index] = new_section
        self.__log_section(self.section_index)
        self.section_index += 1

    def __add_point(self, point: dict) -> None:
        """
        Adds a point to the points variable and increases the index.
        Args:
            point (dict): Containing:
                - km (float): Registration kilometre.
                - properties (dict): All properties that belong to the section.
                - geometry (Point): The geometry of the point.
        Prints:
            Newly added point properties.
        """
        assert not is_empty(point['Geometrie']), f"Poging om een lege puntgeometrie toe te voegen: {point}"

        self.points[self.point_index] = point
        self.__log_point(self.point_index)
        self.point_index += 1

    def __log_point(self, index: int) -> None:
        """
        Prints addition LOG for point in self.points at given index.
        Args:
            index (int): Index of point to print info for.
        """
        print(f"[LOG:] Punt {index} toegevoegd: \t"
              f"{self.points[index]['km']:<7.3f} km \t"
              f"{self.points[index]['Rijrichting']}\t"
              f"{self.points[index]['Eigenschappen']} \n"
              f"\t\t\t\t\t\t\t{set_precision(self.points[index]['Geometrie'], 1)}")

    def __log_section(self, index: int) -> None:
        """
        Prints addition LOG for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        print(f"[LOG:] Sectie {index} toegevoegd: \t"
              f"[{self.sections[index]['Km_bereik'][0]:<7.3f}, {self.sections[index]['Km_bereik'][1]:<7.3f}] km \t"
              f"{self.sections[index]['Wegnummer']}\t"
              f"{self.sections[index]['Rijrichting']}\t"
              f"{self.sections[index]['Eigenschappen']} \n"
              f"\t\t\t\t\t\t\t\t{set_precision(self.sections[index]['Geometrie'], 1)}")

    def __log_section_change(self, index: int) -> None:
        """
        Prints change LOG for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        print(f"[LOG:] Sectie {index} veranderd:  \t"
              f"[{self.sections[index]['Km_bereik'][0]:<7.3f}, {self.sections[index]['Km_bereik'][1]:<7.3f}] km \t"
              f"{self.sections[index]['Wegnummer']}\t"
              f"{self.sections[index]['Rijrichting']}\t"
              f"{self.sections[index]['Eigenschappen']} \n"
              f"\t\t\t\t\t\t\t\t{set_precision(self.sections[index]['Geometrie'], 1)}")

    def __get_overlapping_sections(self, section_a: dict) -> list[dict]:
        """
        Finds all sections within self which overlap with the provided section
        and returns them in a list.
        Args:
            section_a (dict): All data pertaining to a section.
        Returns:
            A list of overlap section data, sorted by start_km depending on
            the driving direction of one of the other sections, which is assumed
            to be representative for all other sections.
        """
        overlapping_sections = []
        for section_b_index, section_b in self.sections.items():
            # First, dismiss all sections which have a non-overlapping range,
            # which prevents the more complex get_overlap() function from being called.
            if determine_range_overlap(section_a['Km_bereik'], section_b['Km_bereik']):
                if get_overlap(section_a['Geometrie'], section_b['Geometrie']):
                    overlapping_sections.append({'index': section_b_index,
                                                 'section_info': section_b})

        if overlapping_sections:
            # For the rest of the implementation, sorting in driving direction is assumed.
            # Thus, sections on the left side should be ordered from high to low ranges.
            rijrichting = overlapping_sections[0]['section_info']['Rijrichting']
            should_reverse = rijrichting == 'L'
            overlapping_sections = sorted(overlapping_sections,
                                          key=lambda x: max(x['section_info']['Km_bereik']),
                                          reverse=should_reverse)

        return overlapping_sections

    @staticmethod
    def get_n_lanes(prop: dict) -> tuple[int, int]:
        """
        Determines the number of lanes given road properties.
        Args:
            prop (dict): Road properties to be evaluated.
        Returns:
            1) The number of main lanes - only 'Rijstrook', 'Splitsing' and 'Samenvoeging' registrations.
            2) The number of lanes, exluding 'puntstuk' registrations.
        """
        main_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                      and lane_type in ['Rijstrook', 'Splitsing', 'Samenvoeging']]
        any_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                     and lane_type not in ['Puntstuk']]
        return len(main_lanes), len(any_lanes)

    def get_sections(self) -> list[dict]:
        """
        Obtain a list of all sections in the road model.
        Returns:
            List of section information.
        """
        return [section for section in self.sections.values()]

    def get_points(self, specifier: str = None) -> list[dict]:
        """
        Obtain a list of all point registrations in the road model.
        The type can be specified as 'MSI', to return only MSI data.
        Returns:
            List of all point information.
        """
        if specifier == 'MSI':
            return [point for point in self.points.values() if 'Rijstroken' in point['Eigenschappen'].keys()]

        return [point for point in self.points.values()]

    def get_local_angle(self, overlapping_ids, point_geom: Point) -> float:
        """
        Find the approximate local angle of sections in the road model at a given point.
        Returns:
            Local angle in degrees.
        """
        overlapping_lines = [line for index, line in self.sections.items() if index in overlapping_ids]

        assert overlapping_lines, f"Punt {point_geom} overlapt niet met lijnen in het model."

        angles = []
        for line in overlapping_lines:
            line_points = [point for point in line['Geometrie'].coords]
            closest_point = min(line_points, key=lambda coord: distance(point_geom, Point(coord)))
            closest_index = line_points.index(closest_point)

            if closest_index + 1 < len(line_points):
                next_point = line_points[closest_index + 1]
            else:
                next_point = line_points[closest_index]  # Middle point

            if closest_index - 1 >= 0:
                previous_point = line_points[closest_index - 1]
            else:
                previous_point = line_points[closest_index]  # Middle point

            if next_point == previous_point:
                print(f"[WAARSCHUWING:] Geen lokale hoek gevonden voor {line}")
                continue

            delta_x = next_point[0] - previous_point[0]
            delta_y = next_point[1] - previous_point[1]

            angle_rad = math.atan2(delta_y, delta_x)
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)

        # Drop the outlier angle from the list in case there are three (or more?)
        if len(angles) > 2:
            median_angle = sorted(angles)[1]
            differences = [abs(angle - median_angle) for angle in angles]
            outlier_index = differences.index(max(differences))
            if max(differences) > 10:
                angles.pop(outlier_index)

        average_angle = sum(angles) / len(angles)
        return average_angle

    def get_section_info_at(self, km: float, side: str) -> list[dict]:
        """
        Finds the full properties of a road section at a specific km and rijrichting.
        Args:
            km (float): Kilometer point to retrieve the road section properties for.
            side (str): Side of the road to retrieve the road section properties for.
        Returns:
            list[dict]: Attributes of the road section(s) at the specified kilometer point.
        """
        section_info = []
        for section in self.sections.values():
            in_selection = (section['Rijrichting'] == side and
                            min(section['Km_bereik']) <= km <= max(section['Km_bereik']))
            if in_selection:
                section_info.append(section)
        return section_info

    def get_properties_at(self, km: float, rijrichting: str) -> dict | list[dict]:
        """
        Prints the properties of a road section at a specific km and rijrichting.
        Args:
            km (float): Kilometer point to retrieve the road section properties for.
            rijrichting (str): Side of the road to retrieve the road section properties for.
        Prints:
            Road section(s) properties.
        Returns:
            list[dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        section_info = self.get_section_info_at(km, rijrichting)
        if len(section_info) > 1:
            print(f"Eigenschappen in rijrichting {rijrichting}, op {km} km:")
            for index, section in enumerate(section_info):
                print(f"    {index}) {section['Eigenschappen']}")
            print("")
            return section_info
        elif len(section_info) == 1:
            print(f"Eigenschappen in rijrichting {rijrichting}, op {km} km: {section_info[0]['Eigenschappen']}\n")
            return section_info[0]['Eigenschappen']
        else:
            print(f"Geen secties gevonden met rijrichting {rijrichting} en {km} km.\n")
            return section_info

    def get_sections_at_point(self, point: Point) -> dict[int: dict]:
        """
        Prints the properties of a road section at a specific point.
        Assumes that only one section is close to the point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict[int, dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        return {index: section for index, section in self.sections.items() if dwithin(point, section['Geometrie'], 0.1)}

    def get_one_section_info_at_point(self, point: Point) -> dict:
        """
        Prints the properties of a road section at a specific point.
        Assumes that only one section is close to the point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict: Attributes of the (first) road section at the specified kilometer point.
        """
        for section in self.sections.values():
            if dwithin(point, section['Geometrie'], 0.1):
                return section
        return {}


def get_km_length(km: list[float]) -> int:
    """
    Determines the distance (in meters) covered by a range given in km.
    The order of km1 and km2 does not matter.
    Args:
        km (list): Range list of format [km1, km2]
    Returns:
        Distance in meters between km1 and km2.
    """
    return round(1000 * abs(km[1] - km[0]))


def determine_range_overlap(range1: list, range2: list) -> bool:
    """
    Determines whether there is overlap between two ranges.
    Args:
        range1 (list): First range with two float values.
        range2 (list): Second range with float values.
    Returns:
        Boolean value indicating whether the sections overlap or not.
        Touching ranges such as [4, 7] and [7, 8] return False.
    """
    min1, max1 = min(range1), max(range1)
    min2, max2 = min(range2), max(range2)
    overlap = max(min1, min2) < min(max1, max2)
    return overlap


def same_direction(geom1: LineString, geom2: LineString) -> bool:
    """
    Determines whether two LineString geometries are in the same direction.
    The assumption is made that the lines overlap in such a way that a
    projection of one point on another line is accurate.
    Args:
        geom1: The first shapely LineString geometry.
        geom2: The second shapely LineString geometry.
    Returns:
        Boolean value that is True when the geometries are in the same direction.
    """
    if geom1.length <= geom2.length:
        small_geom = geom1
        large_geom = geom2
    else:
        small_geom = geom2
        large_geom = geom1

    linedist_a = line_locate_point(large_geom, Point(small_geom.coords[0]))
    linedist_b = line_locate_point(large_geom, Point(small_geom.coords[-1]))

    if linedist_a == linedist_b:
        raise Exception(f"same_direction() kan geen richting bepalen met deze lijnafstanden: {linedist_a, linedist_b}")

    return linedist_a < linedist_b


def get_overlap(geom1: LineString, geom2: LineString) -> LineString | None:
    """
    Finds the overlap geometry between two Shapely geometries.
    Args:
        geom1 (LineString): The first Shapely LineString.
        geom2 (LineString): The second Shapely LineString.
    Returns:
        LineString describing the overlap geometry.
        Returns None if there is no overlap geometry.
    Note:
        The function uses the `intersection` method from Shapely to
        compute the overlap between the two LineString geometries.
        If the geometries do not overlap or have only a Point of
        intersection, the function returns None.
    """
    overlap_geometry = intersection(geom1, geom2, grid_size=GRID_SIZE)

    if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
        return line_merge(overlap_geometry)
    elif isinstance(overlap_geometry, LineString) and not overlap_geometry.is_empty:
        return overlap_geometry
    else:
        return None


def get_first_remainder(geom1: LineString, geom2: LineString) -> LineString:
    """
    Finds the first geometry that two Shapely LineStrings do NOT have in common.
    Args:
        geom1 (LineString): The first Shapely LineString.
        geom2 (LineString): The second Shapely LineString.
    Returns:
        A LineString describing the difference geometry between the two
        provided sections. If there are two options, the first remainder
        option is returned, based on the directional order of geom1.
    """
    diff = difference(geom1, geom2, grid_size=GRID_SIZE)

    if isinstance(diff, LineString) and not diff.is_empty:
        return diff
    elif isinstance(diff, MultiLineString) and not diff.is_empty:
        diffs = [geom for geom in diff.geoms]
        if get_num_geometries(diff) > 2:
            print(f"[WAARSCHUWING:] Meer dan 2 geometrieën resterend. Extra geometrieën: {diffs[2:]}\n")
        # Return the first geometry (directional order of geom1 is maintained)
        return diffs[0]
    else:
        raise Exception(f"Kan niet verder. Lege of onjuiste overgebleven geometrie: {diff}")


class MSIRow:
    def __init__(self, msi_network, msi_row_info: dict, local_road_info: dict):
        self.msi_network = msi_network
        self.info = msi_row_info
        self.properties = self.info['Eigenschappen']
        self.local_road_info = local_road_info
        self.local_road_properties = self.local_road_info['Eigenschappen']
        self.name = f"{self.info['Wegnummer']}{self.info['Rijrichting']}:{self.info['km']}"
        self.lane_numbers = []
        self.n_lanes = 0
        self.n_msis = 0
        self.MSIs = {}
        self.cw = {}
        self.downstream = {}
        self.upstream = {}

    def fill_row_properties(self):
        # Determine everything there is to know about the road in general
        self.lane_numbers = sorted([lane_nr for lane_nr, lane_type in self.local_road_properties.items()
                                    if isinstance(lane_nr, int) and lane_type not in ['Puntstuk']])
        self.n_lanes = len(self.lane_numbers)
        self.n_msis = len(self.properties['Rijstroken'])

        # Create all MSIs in row, passing the parent row class as argument
        self.MSIs = {msi_numbering: MSI(self, msi_numbering) for msi_numbering in self.properties['Rijstroken']}

        # Determine carriageways based on road properties
        self.cw = {}
        cw_index = 1
        lanes_in_current_cw = [1]

        for lane_number in self.lane_numbers:
            # Add final lane and stop
            if lane_number == self.n_lanes:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                break

            current_lane = self.local_road_properties[lane_number]
            next_lane = self.local_road_properties[lane_number + 1]
            if current_lane == next_lane:
                lanes_in_current_cw.append(lane_number + 1)
            else:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                lanes_in_current_cw = [lane_number + 1]
                cw_index += 1

    def determine_msi_row_relations(self):
        downstream_rows = self.msi_network.travel_roadmodel(self, True)

        print(f"Stroomafwaarts van {self.name} is")
        for row in downstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    print(msi_row.name, desc)
                    self.downstream[msi_row] = desc
        print("")

        upstream_rows = self.msi_network.travel_roadmodel(self, False)

        print(f"Stroomopwaarts van {self.name} is")
        for row in upstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    print(msi_row.name, desc)
                    self.upstream.update({msi_row: desc})
        print("")

    def fill_msi_properties(self):
        for msi in self.MSIs.values():
            msi.fill_properties()


class MSINetwork:
    def __init__(self, roadmodel: RoadModel):
        self.roadmodel = roadmodel
        msi_data = self.roadmodel.get_points('MSI')

        self.MSIrows = [MSIRow(self, msi_row, self.roadmodel.get_one_section_info_at_point(msi_row['Geometrie']))
                        for row_numbering, msi_row in enumerate(msi_data)]

        for msi_row in self.MSIrows:
            msi_row.fill_row_properties()

        # These can only be called once all msi_rows are initialised.
        for msi_row in self.MSIrows:
            msi_row.determine_msi_row_relations()
            msi_row.fill_msi_properties()

    def travel_roadmodel(self, msi_row: MSIRow, downstream: bool) -> list:
        current_location = msi_row.info['Geometrie']
        current_km = msi_row.info['km']
        rijrichting = msi_row.local_road_info['Rijrichting']

        start_sections = self.roadmodel.get_sections_at_point(current_location)

        if len(start_sections) == 1:
            starting_section_id = next(iter(start_sections.keys()))  # Obtain first (and only) ID in dict.

        elif len(start_sections) > 1:
            print("[WAARSCHUWING:] Meer dan één sectie gevonden op MSI locatie.")  # Filter the correct ID in dict.
            if (downstream and rijrichting == 'R') or (not downstream and rijrichting == 'L'):
                for section_id, section in start_sections.items():
                    if section['Km_bereik'][0] == current_km:
                        starting_section_id = section_id
                        break
            if (downstream and rijrichting == 'L') or (not downstream and rijrichting == 'R'):
                for section_id, section in start_sections.items():
                    if section['Km_bereik'][1] == current_km:
                        starting_section_id = section_id
                        break

        print(f"Starting recursive search for {starting_section_id}, {current_km}, {downstream}, {rijrichting}")
        msis = self.find_msi_recursive(starting_section_id, current_km, downstream, rijrichting)

        if isinstance(msis, dict):
            return [msis]
        return msis

    def find_msi_recursive(self, current_section_id: int, current_km: float, downstream: bool,
                           rijrichting: str, offset: int = 0, current_distance: float = 0) -> list | dict:
        other_points_on_section, msis_on_section = (
            self.evaluate_section_points(current_section_id, current_km, rijrichting, downstream))

        current_section = self.roadmodel.sections[current_section_id]
        current_distance += current_section['Geometrie'].length
        print(f"Current depth: {current_distance}")

        # Base case 1: Single MSI row found
        if len(msis_on_section) == 1:
            print(f"Single MSI row found on {current_section_id}: {msis_on_section[0]['km']}")
            return {self.get_msi_row_at_point(msis_on_section[0]): offset}

        # Base case 2: Multiple MSI rows found
        if len(msis_on_section) > 1:
            print(f"Multiple MSI rows found on {current_section_id}. Picking the closest one: {msis_on_section[0]['km']}")
            nearest_msi = min(msis_on_section, key=lambda msi: abs(current_km - msi['km']))
            return {self.get_msi_row_at_point(nearest_msi): offset}

        # Base case 3: Maximum depth reached
        if current_distance >= MSI_RELATION_MAX_SEARCH_DISTANCE:
            print(f"The maximum depth was exceeded on this search: {current_distance}")
            return {None: offset}

        # Recursive case 1: No other points on the section
        if not other_points_on_section:
            print(f"No other points on {current_section_id}")
            # Obtain connection point of section
            if downstream:
                connecting_section_ids = [sid for sid, sinfo in self.roadmodel.sections.items() if
                                          dwithin(Point(sinfo['Geometrie'].coords[0]),
                                                  Point(current_section['Geometrie'].coords[-1]), 0.1)]

            else:
                connecting_section_ids = [sid for sid, sinfo in self.roadmodel.sections.items() if
                                          dwithin(Point(sinfo['Geometrie'].coords[-1]),
                                                  Point(current_section['Geometrie'].coords[0]), 0.1)]

            if not connecting_section_ids:
                # There are no further sections connected to the current one. Return empty-handed.
                print(f"No connections at all with {current_section_id}")
                return {None: offset}
            elif len(connecting_section_ids) > 1:
                print(f"It seems that more than one section is connected to {current_section_id}: {connecting_section_ids}")
                # This is likely an intersection. These are of no interest for MSI relations.
                return {None: offset}
            else:
                # Find an MSI in the next section
                print(f"Looking for MSI row in the next section, {connecting_section_ids[0]}")
                return self.find_msi_recursive(connecting_section_ids[0], current_km, downstream, rijrichting, offset, current_distance)

        assert len(other_points_on_section) == 1, f"Onverwacht aantal punten op lijn: {other_points_on_section}"

        # Recursive case 2: *vergence point on the section
        other_point = other_points_on_section[0]
        downstream_split = downstream and other_point['Eigenschappen']['Type'] in ['Splitsing', 'Uitvoeging']
        upstream_split = not downstream and other_point['Eigenschappen']['Type'] in ['Samenvoeging', 'Invoeging']

        if not (downstream_split or upstream_split):
            # The recursive function can be called once, for the (only) section that is in the travel direction.
            if downstream:
                section_id = other_point['Eigenschappen']['Uitgaande_Secties'][0]
                if 'Puntstuk' not in current_section['Eigenschappen'].values():
                    # we are section b. determine annotation.
                    other_section_id = [sid for sid in other_point['Eigenschappen']['Ingaande_Secties'] if sid != current_section_id][0]
                    n_lanes_other, _ = self.roadmodel.get_n_lanes(self.roadmodel.sections[other_section_id]['Eigenschappen'])
                    offset = offset + n_lanes_other
            else:
                section_id = other_point['Eigenschappen']['Ingaande_Secties'][0]
                if 'Puntstuk' not in current_section['Eigenschappen'].values():
                    # we are section b. determine annotation.
                    other_section_id = [sid for sid in other_point['Eigenschappen']['Uitgaande_Secties'] if sid != current_section_id][0]
                    n_lanes_other, _ = self.roadmodel.get_n_lanes(self.roadmodel.sections[other_section_id]['Eigenschappen'])
                    offset = offset + n_lanes_other

            print(f"The *vergence point leads to section {section_id}")
            print(f"Marking {section_id} with +{offset}")

            return self.find_msi_recursive(section_id, other_point['km'], downstream, rijrichting, offset, current_distance)

        if upstream_split:
            section_ids = other_point['Eigenschappen']['Ingaande_Secties']
            print(f"The *vergence point is an upstream split into {section_ids}")

        elif downstream_split:
            section_ids = other_point['Eigenschappen']['Uitgaande_Secties']
            print(f"The *vergence point is a downstream split into {section_ids}")

        potential_cont_section = self.roadmodel.sections[section_ids[0]]
        potential_div_section = self.roadmodel.sections[section_ids[1]]
        if 'Puntstuk' in potential_cont_section['Eigenschappen'].values():
            section_a = section_ids[0]
            section_b = section_ids[1]
            offset_b, _ = self.roadmodel.get_n_lanes(potential_cont_section['Eigenschappen'])
        else:
            section_a = section_ids[1]
            section_b = section_ids[0]
            offset_b, _ = self.roadmodel.get_n_lanes(potential_div_section['Eigenschappen'])

        # Store negative value in this direction.
        print(f"Marking {section_b} with -{offset_b}")

        # Make it do the recursive function twice. Then store the result.
        option_continuation = self.find_msi_recursive(section_a, other_point['km'], downstream, rijrichting, offset, current_distance)
        option_diversion = self.find_msi_recursive(section_b, other_point['km'], downstream, rijrichting, offset - offset_b, current_distance)
        # Return a list of dictionaries
        return [option_continuation, option_diversion]

    def evaluate_section_points(self, current_section_id: int, current_km: float, rijrichting: str, downstream: bool):
        # Only takes points that are upstream/downstream of current point.
        if rijrichting == 'L' and downstream or rijrichting == 'R' and not downstream:
            other_points_on_section = [point_data for point_data in self.roadmodel.get_points() if
                                       current_section_id in point_data['section_ids'] and point_data['km'] < current_km]
        else:
            other_points_on_section = [point_data for point_data in self.roadmodel.get_points() if
                                       current_section_id in point_data['section_ids'] and point_data['km'] > current_km]

        # Further filters for MSIs specifically
        msis_on_section = [point for point in other_points_on_section if
                           point['Eigenschappen']['Type'] == 'Signalering']

        return other_points_on_section, msis_on_section

    def get_msi_row_at_point(self, point: dict) -> MSIRow:
        # Return the MSI row with the same kilometer registration
        for msi_row in self.MSIrows:
            if msi_row.info['km'] == point['km']:
                return msi_row


class MSILegends:
    # All possible legends.
    CROSS = 210
    RIGHT_ARROW = 209
    LEFT_ARROW = 208
    SPEED_50 = 16
    SPEED_50_FLASHERS = 15
    SPEED_50_REDRING = 14
    SPEED_70 = 13
    SPEED_70_FLASHERS = 12
    SPEED_70_REDRING = 11
    SPEED_80 = 10
    SPEED_80_FLASHERS = 9
    SPEED_80_REDRING = 8
    SPEED_90 = 7
    SPEED_90_FLASHERS = 6
    SPEED_90_REDRING = 5
    SPEED_100 = 4
    SPEED_ABOVE_100 = 3  # Blank screen
    GREEN_ARROW = 2
    END_OF_RESTRICTIONS = 1
    BLANK = 0

    # Legend set definitions
    displayset_all = {CROSS,
                      RIGHT_ARROW,
                      LEFT_ARROW,
                      SPEED_50, SPEED_50_FLASHERS, SPEED_50_REDRING,
                      SPEED_70, SPEED_70_FLASHERS, SPEED_70_REDRING,
                      SPEED_80, SPEED_80_FLASHERS, SPEED_80_REDRING,
                      SPEED_90, SPEED_90_FLASHERS, SPEED_90_REDRING,
                      SPEED_100,
                      SPEED_ABOVE_100,
                      GREEN_ARROW,
                      END_OF_RESTRICTIONS,
                      BLANK}
    displayset_leftmost = displayset_all - {LEFT_ARROW}
    displayset_rightmost = displayset_all - {RIGHT_ARROW}


class MSI(MSILegends):
    def __init__(self, parent_msi_row: MSIRow, lane_number: int):
        self.row = parent_msi_row

        # Store all that is unique to the MSI
        self.lane_number = lane_number
        self.displayoptions = self.displayset_all
        self.name = f"{self.row.name}:{str(lane_number)}"

        self.properties = {
            # 'RSU': None,  # RSU name [Not available]
            'c': None,  # Current MSI (center)
            'r': None,  # MSI right
            'l': None,  # MSI left
            'd': None,  # MSI downstream
            'ds': None,  # MSI downstream secondary
            'dt': None,  # MSI downstream taper
            'db': None,  # MSI downstream ExtraRijstrook
            'dn': None,  # MSI downstream Rijstrookbeëindiging
            'u': None,  # MSI upstream
            'us': None,  # MSI upstream secondary
            'ut': None,  # MSI upstream taper
            'ub': None,  # MSI upstream ExtraRijstrook
            'un': None,  # MSI upstream Rijstrookbeëindiging

            'STAT_V': None,  # Static maximum speed
            'C_X': None,  # True if continue-X relation
            'C_V': None,  # True if continue-V relation

            'N_row': None,  # [~] Number of MSIs in row.
            'N_TS': None,  # Number of MSIs in traffic stream.
            'N_CW': None,  # Number of MSIs in carriageway.

            'CW': None,  # All MSIs in CW.
            'CW_num': None,  # CW numbering.
            'CW_right': None,  # All MSIs in CW to the right.
            'CW_left': None,  # All MSIs in CW to the left.

            'TS': None,  # All MSIs in TS.
            'TS_num': None,  # TS numbering.
            'TS_right': None,  # All MSIs in TS to the right.
            'TS_left': None,  # All MSIs in TS to the left.

            'DIF_V_right': None,  # DIF-V influence from the right
            'DIF_V_left': None,  # DIF-V influence from the left

            'row': None,  # All MSIs in row.

            'RHL': None,  # [V] True if MSI in RHL. (Any lane that is open sometimes)
            'Exit_Entry': None,  # True if MSI in RHL and normal lanes left and right.
            'RHL_neighbor': None,  # [V] True if RHL in row.

            'Hard_shoulder_right': None,  # [V] True if hard shoulder directly to the right.
            'Hard_shoulder_left': None,  # [V] True if hard shoulder directly to the left.

            # 'State': None,  # Active legend. [Not applicable]
        }

    def fill_properties(self):
        self.determine_properties()
        self.determine_relations()

        filtered_properties = {key: value for key, value in self.properties.items() if value is not None}
        print(f"{self.name} heeft de volgende eigenschappen:\n{filtered_properties}")
        print("")

    def determine_properties(self):
        self.properties['STAT_V'] = self.row.local_road_properties['Maximumsnelheid']
        # self.properties['C_X'] =
        # self.properties['C_V'] =

        self.properties['N_row'] = self.row.n_msis

        cw_number = None
        for index, names in self.row.cw.items():
            if self.name in names:
                cw_number = index
                break

        if cw_number:
            self.properties['N_CW'] = len(self.row.cw[cw_number])
            self.properties['N_TS'] = self.properties['N_CW']

            self.properties['CW'] = self.row.cw[cw_number]
            self.properties['CW_num'] = cw_number
            self.properties['CW_right'] = self.row.cw[cw_number + 1] if cw_number + 1 in self.row.cw.keys() else None
            self.properties['CW_left'] = self.row.cw[cw_number - 1] if cw_number - 1 in self.row.cw.keys() else None

            # Assumption: traffic stream == carriageway
            self.properties['TS'] = self.properties['CW']
            self.properties['TS_num'] = self.properties['CW_num']
            self.properties['TS_right'] = self.properties['CW_right']
            self.properties['TS_left'] = self.properties['CW_left']

        # Safest assumption: 0 for both directions. DIF_V heeft evt. richtlijnen (bv 20 naar links, 0 naar rechts).
        self.properties['DIF_V_right'] = 0
        self.properties['DIF_V_left'] = 0

        self.properties['row'] = [msi.name for msi in self.row.MSIs.values()]

        if self.row.local_road_properties[self.lane_number] in ['Spitsstrook', 'Plusstrook', 'Bufferstrook']:
            self.properties['RHL'] = True

        if (self.row.local_road_properties[self.lane_number] in ['Spitsstrook', 'Plusstrook', 'Bufferstrook'] and
                self.row.n_lanes > self.lane_number > 1):
            self.properties['Exit-entry'] = True

        if ('Spitsstrook' in self.row.local_road_properties.values() or
                'Plusstrook' in self.row.local_road_properties.values() or
                'Bufferstrook' in self.row.local_road_properties.values()):
            self.properties['RHL_neighbor'] = True

        if self.lane_number < self.row.n_lanes and self.row.local_road_properties[self.lane_number + 1] == 'Vluchtstrook':
            self.properties['Hard_shoulder_right'] = True
        if self.lane_number > 1 and self.row.local_road_properties[self.lane_number - 1] == 'Vluchtstrook':
            self.properties['Hard_shoulder_left'] = True

    def determine_relations(self):
        self.properties['c'] = self.name
        if self.lane_number + 1 in self.row.MSIs.keys():
            self.properties['r'] = self.row.MSIs[self.lane_number + 1].name
        if self.lane_number - 1 in self.row.MSIs.keys():
            self.properties['l'] = self.row.MSIs[self.lane_number - 1].name

        for downstream_row, desc in self.row.downstream.items():
            if self.lane_number + desc in downstream_row.MSIs.keys():
                self.properties['d'] = downstream_row.MSIs[self.lane_number + desc].name

        for upstream_row, desc in self.row.upstream.items():
            if self.lane_number + desc in upstream_row.MSIs.keys():
                self.properties['u'] = upstream_row.MSIs[self.lane_number + desc].name
