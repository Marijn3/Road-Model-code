import geopandas as gpd
import pandas as pd
from shapely import *
import csv
from copy import deepcopy
import math

pd.set_option('display.max_columns', None)
GRID_SIZE = 0.00001


class DataFrameLoader:
    """
   A class for loading GeoDataFrames from shapefiles based on a specified location extent.

   Attributes:
       __LOCATIONS_CSV_PATH (str): The file path for the locations csv file.
       __FILE_PATHS (list): List of file paths for shapefiles to be loaded.
       data (dict): Dictionary to store GeoDataFrames for each layer.
       extent (box): The extent of the specified location.
   """

    __LOCATIONS_CSV_PATH = 'data/locations.csv'

    # List all data layer files to be loaded. Same structure as WEGGEG.
    __FILE_PATHS = [
        "data/Rijstroken/rijstroken-edit.dbf",
        "data/Kantstroken/kantstroken.dbf",
        "data/Mengstroken/mengstroken.dbf",
        "data/Maximum snelheid/max_snelheden.dbf",
        "data/Convergenties/convergenties.dbf",
        "data/Divergenties/divergenties.dbf",
        "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    def __init__(self, location: str) -> None:
        self.data = {}
        self.extent = None
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
            raise ValueError(f"Invalid place: {location}. Please provide a valid location.")

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

    def __edit_columns(self, name: str) -> None:
        """
        Edits columns of GeoDataFrames in self.data in place.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        # Applies some rounding to geometry
        # self.data[name]['geometry'] = self.data[name]['geometry'].apply(lambda geom: set_precision(geom, GRID_SIZE))

        # These column variable types should be changed.
        self.data[name]['WEGNUMMER'] = pd.to_numeric(self.data[name]['WEGNUMMER'], errors='coerce').astype('Int64')

        # Mapping from lane registration to (nLanes, Special feature)
        lane_mapping_h = {'1 -> 1': (1, None), '1 -> 2': (2, 'Broadening'), '2 -> 1': (2, 'Narrowing'),
                          '1 -> 1.6': (1, 'TaperStart'), '1.6 -> 1': (1, 'TaperEnd'),
                          '2 -> 1.6': (2, 'TaperStart'), '1.6 -> 2': (2, 'TaperEnd'),
                          '2 -> 2': (2, None), '2 -> 3': (3, 'Broadening'), '3 -> 2': (3, 'Narrowing'),
                          '3 -> 3': (3, None), '3 -> 4': (4, 'Broadening'), '4 -> 3': (4, 'Narrowing'),
                          '4 -> 4': (4, None), '4 -> 5': (5, 'Broadening'), '5 -> 4': (5, 'Narrowing'),
                          '5 -> 5': (5, None), '5 -> 6': (6, 'Broadening'), '6 -> 5': (6, 'Narrowing'),
                          '6 -> 6': (6, None),
                          '7 -> 7': (7, None)}
        # All registrations with T as kantcode as marked in the opposite direction.
        lane_mapping_t = {'1 -> 1': (1, None), '1 -> 2': (2, 'Narrowing'), '2 -> 1': (2, 'Broadening'),
                          '1 -> 1.6': (1, 'TaperEnd'), '1.6 -> 1': (1, 'TaperStart'),
                          '2 -> 1.6': (2, 'TaperEnd'), '1.6 -> 2': (2, 'TaperStart'),
                          '2 -> 2': (2, None), '2 -> 3': (3, 'Narrowing'), '3 -> 2': (3, 'Broadening'),
                          '3 -> 3': (3, None), '3 -> 4': (4, 'Narrowing'), '4 -> 3': (4, 'Broadening'),
                          '4 -> 4': (4, None), '4 -> 5': (5, 'Narrowing'), '5 -> 4': (5, 'Broadening'),
                          '5 -> 5': (5, None), '5 -> 6': (6, 'Narrowing'), '6 -> 5': (6, 'Broadening'),
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
                    if row['location'] == location:
                        return {
                            'north': float(row['north']),
                            'east': float(row['east']),
                            'south': float(row['south']),
                            'west': float(row['west']),
                        }
            return {}  # Return empty dictionary if the location is not found
        except FileNotFoundError:
            raise FileNotFoundError(f"File was not found: {DataFrameLoader.__LOCATIONS_CSV_PATH}")
        except csv.Error as e:
            raise ValueError(f"Error reading csv file: {e}")


class RoadModel:
    __LAYER_NAMES = ['Rijstroken', 'Kantstroken', 'Mengstroken', 'Maximum snelheid',
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
            The 'Rijstroken' layer is the first layer to be imported because two assumptions hold for it:
                1) it is defined everywhere where it would be necessary.
                2) it does not have internal overlap.
            Additionally, it is the most reliable source for roadside. The only other candidate
            is maximumsnelheden, but this unfortunately sometimes has places where it is
            undefined, therefore the first assumption doesn't hold.
        """
        for df_name in self.__LAYER_NAMES:
            print(f"[STATUS:] Importing {df_name}...")
            current_sections = self.section_index
            current_points = self.point_index

            self.__import_dataframe(dfl, df_name)

            print(f"[STATUS:] {df_name} added {self.section_index - current_sections} sections "
                  f"and {self.point_index - current_points} points to the road model.\n"
                  f"The model has {self.section_index} sections and {self.point_index} points in total.\n")

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

        if name == 'Convergenties':
            properties['Type'] = VERGENCE_TYPE_MAPPING.get(row['TYPE_CONV'], "Unknown")

        if name == 'Divergenties':
            properties['Type'] = VERGENCE_TYPE_MAPPING.get(row['TYPE_DIV'], "Unknown")

        if name == 'Rijstrooksignaleringen':
            properties['Type'] = 'Signalering'
            properties['Rijstroken'] = [int(char) for char in row['RIJSTRKNRS']]

        # Get the roadside letter
        overlapping_sections = self.get_sections_at_point(row['geometry'])
        roadside = [section_info['roadside'] for section_info in overlapping_sections.values()][0]
        roadnumber = [section_info['roadnumber'] for section_info in overlapping_sections.values()][0]

        # Get the IDs of the sections it overlaps
        section_ids = [section_id for section_id in overlapping_sections.keys()]

        # Get the local number of (main) lanes. Take the highest value if there are multiple.
        lane_info = [self.get_n_lanes(section_info['properties']) for section_info in overlapping_sections.values()]
        properties['nMainLanes'] = max(lane_info, key=lambda x: x[0])[0]
        properties['nTotalLanes'] = max(lane_info, key=lambda x: x[1])[1]

        # Get the local orientation
        properties['Local angle'] = self.get_local_angle(section_ids, row['geometry'])

        return {'roadside': roadside,
                'roadnumber': roadnumber,
                'km': row['KMTR'],
                'section_ids': section_ids,
                'properties': properties,
                'geometry': row['geometry']}

    @staticmethod
    def __extract_line_properties(row: pd.Series, name: str):
        properties = {}
        roadside = None
        roadnumber = None

        if name == 'Rijstroken':
            first_lane_number = row['VNRWOL']
            n_lanes, special = row['laneInfo']

            # Indicate lane number and type of lane. Example: {1: 'Rijstrook', 2: 'Rijstrook'}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                properties[lane_nr] = 'Rijstrook'

            # Take note of special circumstances on this feature.
            if special:
                changing_lane = row['VOLGNRSTRK']
                properties['Special'] = (special, changing_lane)

            roadside = row['IZI_SIDE']
            roadnumber = row['WEGNUMMER']

            if roadside == 'R':
                km_range = [row['BEGINKM'], row['EINDKM']]
            else:
                km_range = [row['EINDKM'], row['BEGINKM']]

            return {'roadside': roadside,
                    'roadnumber': roadnumber,
                    'km_range': km_range,
                    'properties': properties,
                    'geometry': set_precision(row['geometry'], GRID_SIZE)}

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

        return {'roadside': roadside,
                'roadnumber': roadnumber,
                'km_range': [row['BEGINKM'], row['EINDKM']],
                'properties': properties,
                'geometry': set_precision(row['geometry'], GRID_SIZE)}

    def __determine_sectioning(self, new_section: dict) -> None:
        """
        Merges the given section with existing sections in self.sections.
        Args:
            new_section (dict): Information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            print(f"No overlap detected with {new_section}. It will not be added.")
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            return

        overlap_section = overlap_sections.pop(0)

        other_section_index = overlap_section['index']
        overlap_section_info = deepcopy(overlap_section['section_info'])

        other_section_side = overlap_section_info['roadside']
        other_section_roadnumber = overlap_section_info['roadnumber']
        other_section_range = overlap_section_info['km_range']
        other_section_props = overlap_section_info['properties']
        other_section_geom = overlap_section_info['geometry']

        new_section_range = new_section['km_range']

        # Align new section range according to existing sections
        if other_section_side == 'L':
            new_section_range.reverse()

        new_section_props = new_section['properties']

        # Ensure all new geometries are also oriented in driving direction
        if same_direction(other_section_geom, new_section['geometry']):
            new_section_geom = new_section['geometry']
        else:
            print("Attention: new geometry is reversed.")
            new_section_geom = reverse(new_section['geometry'])

        sections_to_remove = set()

        while True:

            if not get_overlap(new_section_geom, other_section_geom):
                overlap_section = overlap_sections.pop(0)

                other_section_index = overlap_section['index']
                overlap_section_info = deepcopy(overlap_section['section_info'])

                other_section_range = overlap_section_info['km_range']
                other_section_props = overlap_section_info['properties']
                other_section_geom = overlap_section_info['geometry']

            # print("New section range:", new_section_range)
            # print("New section props:", new_section_props)
            # print("New section geom:", set_precision(new_section['geometry'], 1))
            # print("Other section range:", other_section_range)
            # print("Other section props:", other_section_props)
            # print("Other section geom:", set_precision(other_section_geom, 1))

            assert determine_range_overlap(new_section_range, other_section_range), "Ranges don't overlap."
            if abs(get_km_length(new_section['km_range']) - new_section['geometry'].length) > 100:
                print(
                    f"[WARNING:] Big length difference: {get_km_length(new_section['km_range'])} and {new_section['geometry'].length}\n")

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
                    km_range = [min(new_section_range), min(other_section_range)]
                else:
                    km_range = [max(new_section_range), max(other_section_range)]
                added_geom = get_first_remainder(new_section_geom, other_section_geom)
                self.__add_section({
                    'roadside': other_section_side,
                    'roadnumber': other_section_roadnumber,
                    'km_range': km_range,
                    'properties': new_section_props,
                    'geometry': added_geom
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
                        print(f"[WARNING:] Possibly inconsistent geometries: "
                              f"{new_section_geom} and {other_section_geom}\n")
                    self.__update_section(other_section_index,
                                          km_range=new_section_range,
                                          props=new_section_props,
                                          geom=other_section_geom)
                    # This is the final iteration.
                    break

                # Add section between new_section_min and new_section_max
                # with both properties and overlapping geometry.
                # Update other_section range between new_section_max and other_section_max
                # with and remaining geometry.
                # Remove old other_section.
                elif other_section_larger:
                    if right_side:
                        km_range = [min(new_section_range), max(new_section_range)]
                    else:
                        km_range = [max(new_section_range), min(new_section_range)]

                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    assert added_geom, "No overlap found"
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'roadside': other_section_side,
                        'roadnumber': other_section_roadnumber,
                        'km_range': km_range,
                        'properties': both_props,
                        'geometry': added_geom
                    })
                    if right_side:
                        km_remaining = [max(new_section_range), max(other_section_range)]
                    else:
                        km_remaining = [min(new_section_range), min(other_section_range)]
                    other_geom = get_first_remainder(other_section_geom, added_geom)
                    self.__update_section(other_section_index,
                                          km_range=km_remaining,
                                          geom=other_geom)
                    # This is the final iteration.
                    break

                elif new_section_larger:
                    # Add section with both properties
                    if right_side:
                        km_range = [min(new_section_range), max(other_section_range)]
                    else:
                        km_range = [max(new_section_range), min(other_section_range)]
                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'roadside': other_section_side,
                        'roadnumber': other_section_roadnumber,
                        'km_range': km_range,
                        'properties': both_props,
                        'geometry': added_geom
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
                            'roadside': other_section_side,
                            'roadnumber': other_section_roadnumber,
                            'km_range': new_section_range,
                            'properties': new_section_props,
                            'geometry': new_section_geom
                        })
                        break

                else:
                    raise Exception("Something has gone wrong with the ranges.")

            # Case C: new_section starts later.
            # Add section between other_section_start and new_section_start
            # with other_section properties and geometry.
            elif other_section_first:
                # Add section...
                if right_side:
                    km_range = [min(other_section_range), min(new_section_range)]
                else:
                    km_range = [max(other_section_range), max(new_section_range)]
                added_geom = get_first_remainder(other_section_geom, new_section_geom)
                self.__add_section({
                    'roadside': other_section_side,
                    'roadnumber': other_section_roadnumber,
                    'km_range': km_range,
                    'properties': other_section_props,
                    'geometry': added_geom
                })
                # Trim the other_section range and geometry for next iteration.
                if right_side:
                    other_section_range = [min(new_section_range), max(other_section_range)]
                else:
                    other_section_range = [max(new_section_range), min(other_section_range)]
                other_section_geom = get_first_remainder(other_section_geom, added_geom)

            else:
                raise Exception("Something has gone wrong with the ranges.")

        self.__remove_sections(sections_to_remove)

    def __remove_sections(self, indices: set[int]) -> None:
        """
        Removes sections at the given indices.
        Args:
            indices (set): Set of indices at which to remove sections.
        """
        for index in indices:
            self.sections.pop(index)
            print(f"[LOG:] Section {index} removed.\n")

    def __update_section(self, index: int, km_range: list = None, props: dict = None, geom: LineString = None) -> None:
        """
        Updates one or more properties of a section at a given index.
        Prints log of section update.
        Args:
            index (int): Index of section to be updated
            km_range (list[float]): Start and end registration kilometer. No sorting needed.
            props (dict): All properties that belong to the section.
            geom (LineString): The geometry of the section.
        Prints:
            Changed section properties.
        """
        assert any([km_range, props, geom]), "Update section called, but no update is required."
        assert km_range and geom or not (km_range or geom), "Please provide both km_range and geometry."

        if km_range:
            if abs(get_km_length(km_range) - geom.length) > 100:
                print(f"[WARNING:] Big length difference: {get_km_length(km_range)} and {geom.length}\n")
            self.sections[index]['km_range'] = km_range
        if props:
            self.sections[index]['properties'].update(props)
        if geom:
            self.sections[index]['geometry'] = geom

        self.__log_section_change(index)

    def __add_section(self, new_section: dict) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict): Containing:
                - roadside (str): Side of the road. Either 'R' or 'L'.
                - km_range (list[float]): Start and end registration kilometre.
                - properties (dict): All properties that belong to the section.
                - geometry (LineString): The geometry of the section.
        Prints:
            Newly added section properties.
        """
        assert not is_empty(new_section['geometry']), f"Request to add an empty geometry: {new_section['geometry']}"
        if abs(get_km_length(new_section['km_range']) - new_section['geometry'].length) > 100:
            print(f"[WARNING:] Big length difference: "
                  f"{get_km_length(new_section['km_range'])} and {new_section['geometry'].length}\n")

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
        assert not is_empty(point['geometry']), "Trying to add an empty geometry."

        self.points[self.point_index] = point
        self.__log_point(self.point_index)
        self.point_index += 1

    def __log_point(self, index: int) -> None:
        """
        Prints addition LOG for point in self.points at given index.
        Args:
            index (int): Index of point to print info for.
        """
        print(f"[LOG:] Point {index} added: \t"
              f"{self.points[index]['km']:>7.3f} km \t"
              f"{self.points[index]['roadside']}\t"
              f"{self.points[index]['properties']} \n"
              f"\t\t\t\t\t\t{set_precision(self.points[index]['geometry'], 1)}")

    def __log_section(self, index: int) -> None:
        """
        Prints addition LOG for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        print(f"[LOG:] Section {index} added: \t"
              f"[{self.sections[index]['km_range'][0]:>7.3f}, {self.sections[index]['km_range'][1]:>7.3f}] km \t"
              f"{self.sections[index]['roadside']}\t"
              f"{self.sections[index]['properties']} \n"
              f"\t\t\t\t\t\t\t{set_precision(self.sections[index]['geometry'], 1)}")

    def __log_section_change(self, index: int) -> None:
        """
        Prints change LOG for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        print(f"[LOG:] Section {index} changed: \t"
              f"[{self.sections[index]['km_range'][0]:>7.3f}, {self.sections[index]['km_range'][1]:>7.3f}] km \t"
              f"{self.sections[index]['roadside']}\t"
              f"{self.sections[index]['properties']} \n"
              f"\t\t\t\t\t\t\t{set_precision(self.sections[index]['geometry'], 1)}")

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
            if determine_range_overlap(section_a['km_range'], section_b['km_range']):
                if get_overlap(section_a['geometry'], section_b['geometry']):
                    overlapping_sections.append({'index': section_b_index,
                                                 'section_info': section_b})

        if overlapping_sections:
            # For the rest of the implementation, sorting in driving direction is assumed.
            # Thus, sections on the left side should be ordered from high to low ranges.
            roadside = overlapping_sections[0]['section_info']['roadside']
            should_reverse = roadside == 'L'
            overlapping_sections = sorted(overlapping_sections,
                                          key=lambda x: max(x['section_info']['km_range']),
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
            return [point for point in self.points.values() if 'Rijstroken' in point['properties'].keys()]

        return [point for point in self.points.values()]

    def get_local_angle(self, overlapping_ids, point_geom: Point) -> float:
        """
        Find the approximate local angle of sections in the road model at a given point.
        Returns:
            Local angle in degrees.
        """
        overlapping_lines = [line for index, line in self.sections.items() if index in overlapping_ids]

        assert overlapping_lines, "Point is not overlapping any lines."

        angles = []
        for line in overlapping_lines:
            line_points = [point for point in line['geometry'].coords]
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
                print(f"[WARNING:] Could not find local angle for {line}")
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
        Finds the full properties of a road section at a specific km and roadside.
        Args:
            km (float): Kilometer point to retrieve the road section properties for.
            side (str): Side of the road to retrieve the road section properties for.
        Returns:
            list[dict]: Attributes of the road section(s) at the specified kilometer point.
        """
        section_info = []
        for section in self.sections.values():
            in_selection = (section['roadside'] == side and
                            min(section['km_range']) <= km <= max(section['km_range']))
            if in_selection:
                section_info.append(section)
        return section_info

    def get_properties_at(self, km: float, side: str) -> dict | list[dict]:
        """
        Prints the properties of a road section at a specific km and roadside.
        Args:
            km (float): Kilometer point to retrieve the road section properties for.
            side (str): Side of the road to retrieve the road section properties for.
        Prints:
            Road section(s) properties.
        Returns:
            list[dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        section_info = self.get_section_info_at(km, side)
        if len(section_info) > 1:
            print(f"Properties on side {side}, at {km} km:")
            for index, section in enumerate(section_info):
                print(f"    {index}) {section['properties']}")
            print("")
            return section_info
        elif len(section_info) == 1:
            print(f"Properties on side {side}, at {km} km: {section_info[0]['properties']}\n")
            return section_info[0]['properties']
        else:
            print(f"No sections found on side {side} at {km} km.\n")
            return section_info

    def get_sections_at_point(self, point: Point) -> dict[int: dict]:
        """
        Prints the properties of a road section at a specific point.
        Assumes that only one section is close to the point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            tuple[int, dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        return {index: section for index, section in self.sections.items() if dwithin(point, section['geometry'], 0.1)}

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
            if dwithin(point, section['geometry'], 0.1):
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
    The assumption is made that the lines are close enough together that a
    projection of one point on another line is accurate.
    Geom1 is taken as the 'correct' orientation.
    Args:
        geom1: The first shapely LineString geometry.
        geom2: The second shapely LineString geometry.
    Returns:
        Boolean value that is True when the geometries are in the same directions.
    """
    geom1_linedist_a = line_locate_point(geom1, Point(geom2.coords[0]))
    geom1_linedist_b = line_locate_point(geom1, Point(geom2.coords[-1]))

    # Catch cases where both linedistances are equal (likely 0 or 1)
    if geom1_linedist_a == geom1_linedist_b:
        geom2_linedist_a = line_locate_point(geom2, Point(geom1.coords[0]))
        geom2_linedist_b = line_locate_point(geom2, Point(geom1.coords[-1]))
        return geom2_linedist_a < geom2_linedist_b

    return geom1_linedist_a < geom1_linedist_b


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
            print(f"[WARNING:] More than 2 remaining geometries. Extra geometries: {diffs[2:]}\n")
        # Return the first geometry (directional order of geom1 is maintained)
        return diffs[0]
    else:
        raise Exception(f"Cannot continue. Empty or wrong remaining geometry: {diff}")


class MSIRow:
    def __init__(self, msi_network, msi_row_info: dict, local_road_info: dict):
        self.msi_network = msi_network
        self.info = msi_row_info
        self.properties = self.info['properties']
        self.local_road_info = local_road_info
        self.local_road_properties = self.local_road_info['properties']
        self.name = f"A{self.info['roadnumber']}{self.info['roadside']}:{self.info['km']}"

        # Determine everything there is to know about the road in general
        self.n_lanes = max((lane_nr for lane_nr, lane_type in self.local_road_properties.items()
                            if isinstance(lane_nr, int) and lane_type not in ['Puntstuk']), default=0)
        self.n_msis = len(self.properties['Rijstroken'])

        # Create all MSIs in row, passing the parent row class as argument
        self.MSIs = {msi_numbering: MSI(self, msi_numbering) for msi_numbering in self.properties['Rijstroken']}

        # Determine carriageways based on road properties
        self.cw = {}
        cw_index = 1
        lanes_in_current_cw = [1]

        # TODO: Does NOT work for taper or broadening/narrowing. Assumes whole numbers
        for lane_number in range(1, self.n_lanes):
            current_lane = self.local_road_properties[lane_number]
            next_lane = self.local_road_properties[lane_number + 1]
            if current_lane == next_lane:
                lanes_in_current_cw.append(lane_number + 1)
            else:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                lanes_in_current_cw = [lane_number + 1]
                cw_index += 1

            # Add final lane
            if lane_number + 1 == self.n_lanes:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]

    def fill_row_properties(self):
        for msi in self.MSIs.values():
            msi.fill_msi_properties()


class MSINetwork:
    def __init__(self, roadmodel: RoadModel):
        self.roadmodel = roadmodel
        msi_data = self.roadmodel.get_points('MSI')

        self.MSIrows = [MSIRow(self, msi_row, self.roadmodel.get_one_section_info_at_point(msi_row['geometry']))
                        for row_numbering, msi_row in enumerate(msi_data)]

        for msi_row in self.MSIrows:
            msi_row.fill_row_properties()

    def travel_roadmodel(self, msi_row: MSIRow, downstream: bool = True) -> MSIRow | None:
        # current_location = msi_row.info['geometry']
        # roadmodel_section = self.roadmodel.get_sections_at_point(current_location)
        #
        # # TODO: Ensure that the geometry does not directly intersect another registered point!
        #
        # # Extract the first and last points of the geometry
        # if downstream:
        #     connection_point = roadmodel_section.coords[-1]
        # else:
        #     connection_point = roadmodel_section.coords[0]
        #
        # next_section = ...

        current_km = msi_row.info['km']
        roadside = msi_row.local_road_info['roadside']

        # Filter points based on roadside and travel direction.
        if roadside == 'L' and downstream or roadside == 'R' and not downstream:
            eligible_points = [point for point in self.roadmodel.get_points('MSI') if point['km'] < current_km
                               and point['roadside'] == roadside]
        else:
            eligible_points = [point for point in self.roadmodel.get_points('MSI') if point['km'] > current_km
                               and point['roadside'] == roadside]

        if eligible_points:
            closest_point = min(eligible_points, key=lambda point: abs(current_km - point['km']))

            # Return the MSI row with the same kilometre registration
            for msi_row in self.MSIrows:
                if msi_row.info['km'] == closest_point['km']:
                    return msi_row

        else:
            return None


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
            'c': None,  # Current MSI
            'r': None,  # MSI right
            'l': None,  # MSI left
            'd': None,  # MSI downstream
            'ds': None,  # MSI downstream secondary
            'dt': None,  # MSI downstream taper
            'db': None,  # MSI downstream broadening
            'dn': None,  # MSI downstream narrowing
            'u': None,  # MSI upstream
            'us': None,  # MSI upstream secondary
            'ut': None,  # MSI upstream taper
            'ub': None,  # MSI upstream broadening
            'un': None,  # MSI upstream narrowing

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

            'RHL': None,  # [V] True if MSI in RHL.
            'Exit_Entry': None,  # True if MSI in RHL and normal lanes left and right.
            'RHL_neighbor': None,  # [V] True if RHL in row.

            'Hard_shoulder_right': None,  # [V] True if hard shoulder directly to the right.
            'Hard_shoulder_left': None,  # [V] True if hard shoulder directly to the left.

            # 'State': None,  # Active legend. [Not applicable]
        }

    def fill_msi_properties(self):
        self.determine_MSI_properties()
        self.determine_MSI_relations()

        filtered_properties = {key: value for key, value in self.properties.items() if value is not None}
        print(f"{self.name} has the following properties:\n{filtered_properties}")

    def determine_MSI_properties(self):
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

        # DIF - V heeft richtlijnen (bv 20 naar links, 0 naar rechts)
        # self.properties['DIF_V_right'] =
        # self.properties['DIF_V_left'] =

        self.properties['row'] = [msi.name for msi in self.row.MSIs.values()]

        if self.row.local_road_properties[self.lane_number] in ['Spitsstrook', 'Plusstrook', 'Bufferstrook']:
            self.properties['RHL'] = True
        # self.properties['Exit-entry'] =
        if 'Spitsstrook' in self.row.local_road_properties.values():
            self.properties['RHL_neighbor'] = True

        if self.lane_number < self.row.n_lanes and self.row.local_road_properties[
            self.lane_number + 1] == 'Vluchtstrook':
            self.properties['Hard_shoulder_right'] = True
        if self.lane_number > 1 and self.row.local_road_properties[self.lane_number - 1] == 'Vluchtstrook':
            self.properties['Hard_shoulder_left'] = True

    def determine_MSI_relations(self):
        self.properties['c'] = self.name
        if self.lane_number + 1 in self.row.MSIs.keys():
            self.properties['r'] = self.row.MSIs[self.lane_number + 1].name
        if self.lane_number - 1 in self.row.MSIs.keys():
            self.properties['l'] = self.row.MSIs[self.lane_number - 1].name

        downstream_row = self.row.msi_network.travel_roadmodel(self.row, True)
        if downstream_row and self.lane_number in downstream_row.MSIs.keys():
            self.properties['d'] = downstream_row.MSIs[self.lane_number].name

        upstream_row = self.row.msi_network.travel_roadmodel(self.row, False)
        if upstream_row and self.lane_number in upstream_row.MSIs.keys():
            self.properties['u'] = upstream_row.MSIs[self.lane_number].name
