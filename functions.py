import geopandas as gpd
import pandas as pd
from shapely import *
import csv
from copy import deepcopy

pd.set_option('display.max_columns', None)


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

    # List all data layer files to be loaded.
    __FILE_PATHS = [
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        # "data/Mengstroken/mengstroken.dbf",
        "data/Maximum snelheid/max_snelheden.dbf",
        # "data/Convergenties/convergenties.dbf",
        # "data/Divergenties/divergenties.dbf",
        # "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    def __init__(self):
        self.data = {}
        self.extent = None

    def load_dataframes(self, location: str):
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            location (str): The name of the location.
        """
        self.__get_extent(location)
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

    def __get_extent(self, location: str) -> box:
        """
        Determine the extent box of the specified location from coordinates.
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
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with only data that intersects the extent.
        """
        # All data that intersects extent is considered 'in the extent'.
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

    def __edit_columns(self, name: str):
        """
        Edit columns from the GeoDataFrame.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        # Use 0.01 rounding for cm precision, or 1 for meter precision
        self.data[name]['geometry'] = self.data[name]['geometry'].apply(lambda geom: set_precision(geom, 1))

        # These column variable types should be changed.
        self.data[name]['WEGNUMMER'] = pd.to_numeric(self.data[name]['WEGNUMMER'], errors='coerce').astype('Int64')

        if name == 'Rijstroken':
            lane_mapping = {'1 -> 1': 1, '1 -> 2': 1.1, '2 -> 1': 1.9,
                            '2 -> 2': 2, '2 -> 3': 2.1, '3 -> 2': 2.9,
                            '3 -> 3': 3, '3 -> 4': 3.1, '4 -> 3': 3.9,
                            '4 -> 4': 4, '4 -> 5': 4.1, '5 -> 4': 4.9,
                            '5 -> 5': 5}
            self.data[name]['nRijstroken'] = self.data[name]['OMSCHR'].apply(lambda df: lane_mapping.get(df, df))

            # Convert VOLGNRSTRK to integer, supporting NaN values
            # self.data[df_name]['VOLGNRWOL'] = (
            #     pd.to_numeric(self.data[df_name]['VOLGNRSTRK'], errors='coerce').astype('Int64'))

        if name == 'Mengstroken':
            self.data[name]['nMengstroken'] = self.data[name]['OMSCHR'].apply(lambda df: lane_mapping.get(df, df))

        if name == 'Rijstrooksignaleringen':
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            is_kp = self.data[name]['CODE'] == 'KP'
            self.data[name] = self.data[name][is_kp]

        # These general columns are not further necessary.
        # self.data[df_name].drop(columns=['FK_VELD4', 'IBN', 'inextent'], inplace=True)

        # All 'stroken' dataframes have VNRWOL columns which should be converted to integer.
        if 'stroken' in name:
            self.data[name]['VNRWOL'] = pd.to_numeric(self.data[name]['VNRWOL'], errors='coerce').astype('Int64')

    @staticmethod
    def __load_extent_from_csv(location: str) -> dict:
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
    def __init__(self):
        self.sections = {}
        self.section_index = 0
        self.has_layer = False

    def import_dataframes(self, dfl: DataFrameLoader):
        """
        Load road attributes from all DataFrames.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
        """
        self.__import_dataframe(dfl, 'Rijstroken')
        self.__import_dataframe(dfl, 'Kantstroken')
        self.__import_dataframe(dfl, 'Maximum snelheid')

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str):
        """
        Load road sections and attributes from a DataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
        """
        print('[STATUS:] Importing', df_name, '...')
        current_sections = self.section_index

        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            section_info = self.__extract_row_properties(row, df_name)
            if self.has_layer:
                self.__determine_sectioning(section_info)
            else:
                self.__add_section(section_info)
        self.has_layer = True

        # self.print_section_info()
        print('[STATUS:] Added', self.section_index-current_sections, 'sections. '
              'The model has', self.section_index, 'sections in total.')
        print("")

    def __extract_row_properties(self, row: pd.Series, name: str):
        """
        Turns the contents of a road data Dataframe row into a dictionary with the relevant entries.
        Args:
            row (pd.Series): Row containing information about the road section
            name (str): Name of dataframe.
        """
        if isinstance(row['geometry'], (Point, MultiPoint)):
            return self.__extract_point_properties(row, name)
        else:
            return self.__extract_line_properties(row, name)

    @staticmethod
    def __extract_point_properties(row: pd.Series, name: str):
        properties = {}

        if name == 'Convergenties':
            properties['Type convergentie'] = row['TYPE_CONV']

        if name == 'Divergenties':
            properties['Type divergentie'] = row['TYPE_DIV']

        if name == 'Rijstrooksignaleringen':
            properties['Rijstroken'] = [int(char) for char in row['RIJSTRKNRS']]

        return {'km': row['KMTR'],
                'properties': properties,
                'geometry': row['geometry']}

    @staticmethod
    def __extract_line_properties(row: pd.Series, name: str):
        properties = {}

        if name == 'Rijstroken':
            # Extract some base properties of the road.
            properties = {
                'Baanpositie': row['IZI_SIDE'],
                'Wegnummer': row['WEGNUMMER'],
            }

            first_lane_number = row['VNRWOL']
            n_rijstroken = int(row['nRijstroken'])  # Always rounds down

            # Indicate lane number and type of lane. Example: {1: 'Rijstrook', 2: 'Rijstrook'}
            for lane_number in range(first_lane_number, n_rijstroken+1):
                properties[lane_number] = 'Rijstrook'

        elif name == 'Kantstroken':
            # Indicate lane number and type of kantstrook. Example: {3: 'Spitsstrook'}
            lane_number = row['VNRWOL']
            properties[lane_number] = row['OMSCHR']

        elif name == 'Mengstroken':
            first_lane_number = row['VNRWOL']
            n_mengstroken = int(row['nMengstroken'])  # Always rounds down

            # Indicate lane number and type of mengstrook. Example: {4: 'Weefstrook'}
            for lane_number in range(first_lane_number, n_mengstroken + 1):
                properties[lane_number] = row['OMSCHR']

        elif name == 'Maximum snelheid':
            properties['Maximumsnelheid'] = row['OMSCHR']

        # Flip geometry so the direction is always in the increasing kilometer direction.
        if row['KANTCODE'] == 'T':
            print(f"Reversing {row['geometry']} to {reverse(row['geometry'])}")
            geom = reverse(row['geometry'])
        elif row['KANTCODE'] == 'H':
            geom = row['geometry']
            print("Just adding regularly:", geom)
        else:
            raise Exception(f"The kantcode '{row['KANTCODE']}' is not recognized.")

        return {'km_range': [row['BEGINKM'], row['EINDKM']],
                'properties': properties,
                'geometry': geom}

    def __determine_sectioning(self, new_section: dict):
        """
        Determine how to merge provided section with existing sections.
        Args:
            new_section (dict): All relevant information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            self.__add_section(new_section)
            return

        new_section_range = new_section['km_range']
        new_section_props = new_section['properties']
        new_section_geom = new_section['geometry']

        num_overlap_sections = len(overlap_sections)
        sections_to_remove = set()
        i_overlap = 0
        overlap_section = overlap_sections[i_overlap]

        other_section_index = overlap_section['index']
        overlap_section_info = deepcopy(overlap_section['section_info'])

        other_section_range = overlap_section_info['km_range']
        other_section_props = overlap_section_info['properties']
        other_section_geom = overlap_section_info['geometry']

        while True:  # get_num_coordinates(new_section_geom) != 0:

            if not self.__get_overlap(new_section_geom, other_section_geom):
                print("Moving on to next overlap section.")

                i_overlap += 1

                if i_overlap > num_overlap_sections:
                    print('End reached. [Unexpected]')
                    break

                overlap_section = overlap_sections[i_overlap]

                other_section_index = overlap_section['index']
                overlap_section_info = deepcopy(overlap_section['section_info'])

                other_section_range = overlap_section_info['km_range']
                other_section_props = overlap_section_info['properties']
                other_section_geom = overlap_section_info['geometry']

            print('New section range:', new_section_range)
            print('New section props:', new_section_props)
            print('New section geom:', new_section_geom)

            print('Other section range:', other_section_range)
            print('Other section props:', other_section_props)
            print('Other section geom:', other_section_geom)

            assert self.__determine_range_overlap(new_section_range, other_section_range), "Ranges don't overlap."
            assert same_direction(new_section_geom, other_section_geom), f"Geometries not in the same direction: {new_section_geom}, {other_section_geom}"

            # Case A: new_section starts earlier.
            # Add section between new_section_start and other_section_start
            # with new_section properties and geometry
            if min(new_section_range) < min(other_section_range):
                # Add section...
                added_geom = self.__get_remainder(new_section_geom, other_section_geom)[0]
                self.__add_section({
                    'km_range': [min(new_section_range), min(other_section_range)],
                    'properties': new_section_props,
                    'geometry': added_geom
                })
                # Trim the new_section range and geometry for next iteration.
                new_section_range = [min(other_section_range), max(new_section_range)]
                new_section_geom = self.__get_remainder(added_geom, new_section_geom)[0]
                continue

            # Case B: start is equal.
            elif min(new_section_range) == min(other_section_range):

                # Update the overlapping section properties
                if max(new_section_range) == max(other_section_range):
                    assert new_section_geom.equals(other_section_geom), (
                        f"Inconsistent geometries: {new_section_geom} and {other_section_geom}")
                    self.__update_section(other_section_index,
                                          props=new_section_props)
                    # This is the final iteration.
                    break

                # Add section between new_section_min and new_section_max
                # with both properties and overlapping geometry.
                # Update other_section range between new_section_max and other_section_max
                # with and remaining geometry.
                # Remove old other_section.
                elif max(new_section_range) < max(other_section_range):
                    added_geom = self.__get_overlap(new_section_geom, other_section_geom)
                    assert added_geom, "No overlap found"
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'km_range': [min(new_section_range), max(new_section_range)],
                        'properties': both_props,
                        'geometry': added_geom
                    })
                    other_geom = self.__get_remainder(added_geom, other_section_geom)[0]
                    self.__update_section(other_section_index,
                                          km_range=[max(new_section_range), max(other_section_range)],
                                          geom=other_geom)
                    # This is the final iteration.
                    break

                # Add section between new_section_min and other_section_max
                # with both properties and overlapping geometry.
                # Remove old other_section, since it has now been completely used.
                elif max(new_section_range) > max(other_section_range):
                    added_geom = self.__get_overlap(new_section_geom, other_section_geom)
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        'km_range': [min(new_section_range), max(other_section_range)],
                        'properties': both_props,
                        'geometry': added_geom
                    })
                    # Trim the new_section range and geometry for another go.
                    new_section_range = [max(other_section_range), max(new_section_range)]
                    new_section_geom = self.__get_remainder(new_section_geom, added_geom)[0]
                    # Store old overlap section index to later remove from road model.
                    sections_to_remove.add(other_section_index)

                else:
                    raise Exception("Something has gone wrong with the ranges.")

            # Case C: new_section starts later.
            # Add section between other_section_start and new_section_start
            # with other_section properties and geometry.
            elif min(new_section_range) > min(other_section_range):
                added_geom = self.__get_remainder(new_section_geom, other_section_geom)[0]
                self.__add_section({
                    'km_range': [min(other_section_range), min(new_section_range)],
                    'properties': other_section_props,
                    'geometry': added_geom
                })
                # Trim the other_section range and geometry for next iteration.
                other_section_range = [min(new_section_range), max(other_section_range)]
                other_section_geom = self.__get_remainder(added_geom, other_section_geom)[0]

            else:
                raise Exception("Something has gone wrong with the ranges.")

        self.__remove_sections(sections_to_remove)

    def __remove_sections(self, sections_to_remove: set[int]):
        for section_index in sections_to_remove:
            print("Removing section", section_index)
            self.sections.pop(section_index)

    def __check_overlap(self, geom: LineString, exception_geom: LineString, overlap_sections: list[dict]) -> bool:
        """
        Checks whether the geometry provided overlaps with any
        of the sections in overlap_sections, except for one geometry.
        Args:
            geom (LineString):
            exception_geom (LineString):
            overlap_sections (dict):
        Returns:
            Boolean that indicates whether the geometry overlaps with another section.
        """
        for other_overlap in overlap_sections:
            if other_overlap['geom'] != exception_geom:
                o = self.__get_overlap(geom, other_overlap['geom'])
                if o:
                    return True
        return False

    @staticmethod
    def __determine_range_overlap(range1: list, range2: list) -> bool:
        """
        Determines whether there is overlap between two ranges.
        Args:
            range1 (list): First range with two float values.
            range2 (list): Second range with float values.
        Returns:
            Boolean value indicating whether the sections overlap or not.
            Touching sections such as [4, 7] and [7, 8] return False.
        """
        min1, max1 = min(range1), max(range1)
        min2, max2 = min(range2), max(range2)
        overlap = max(min1, min2) < min(max1, max2)
        return overlap

    def __update_section(self, index: int, km_range: list = None, props: dict = None, geom: LineString = None):
        """
        Updates one or more properties of a section at a given index.
        Prints log of section update.
        Args:
            index (int): Index of section to be updated
            km_range (list[float]): Start and end registration kilometer. No sorting needed.
            props (dict): All properties that belong to the section.
            geom (LineString): The geometry of the section.
        """
        assert any([km_range, props, geom]), 'No update required.'
        assert km_range and geom or not (km_range or geom), ("Warning: please provide both km_range and geometry "
                                                             "if either must be changed.")
        if km_range:
            self.sections[index]['km_range'] = sorted(km_range)
        if props:
            self.sections[index]['properties'].update(props)
        if geom:
            self.sections[index]['geometry'] = geom
        self.__log_section_change(index)

    def __add_section(self, new_section: dict):
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict): Containing:
                - km_range (list[float]): Start and end registration kilometre. Sort by convention before function.
                - properties (dict): All properties that belong to the section.
                - geometry (LineString): The geometry of the section.
        Prints:
            Newly added section properties to log window.
        """
        print("[LOG:] Trying to add section", self.section_index, ":",
              new_section['km_range'],
              new_section['properties'],
              new_section['geometry'])
        assert not is_empty(new_section['geometry']), "Trying to add an empty geometry."

        print(f"Lengths: {get_km_length(new_section['km_range'])} and {new_section['geometry'].length}")
        assert abs(get_km_length(new_section['km_range']) - new_section['geometry'].length) < 100, (
            f"Big length difference: {get_km_length(new_section['km_range'])} and {new_section['geometry'].length}")

        self.sections[self.section_index] = new_section
        self.__log_section(self.section_index)
        self.section_index += 1

    def __log_section(self, index: int):
        print("[LOG:] Section", index, "added:",
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])
        print("")

    def __log_section_change(self, index: int):
        print("[LOG:] Section", index, "changed:",
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])
        print("")

    @staticmethod
    def __get_remainder(geom1: LineString, geom2: LineString) -> list[LineString]:
        """
        Finds the two geometries that two Shapely LineStrings do NOT have in common.
        Args:
            geom1 (LineString): The first Shapely LineString.
            geom2 (LineString): The second Shapely LineString.
        Returns:
            List of two LineStrings describing the geometry that
            is the difference between the two provided sections.
            The order is maintained, so the first item in the list
            contains the first overlap that is encountered.
        """
        remaining_geometry = symmetric_difference(geom1, geom2, grid_size=1)

        if is_empty(remaining_geometry):
            raise Exception(f"Can not continue. Empty remaining geometry: {remaining_geometry}")

        if isinstance(remaining_geometry, LineString):
            return [remaining_geometry]

        if isinstance(remaining_geometry, MultiLineString):
            remaining_geometries = [geom for geom in remaining_geometry.geoms]
            if get_num_geometries(remaining_geometry) > 2:
                sorted_geoms = sorted(remaining_geometries, key=lambda geom: geom.length, reverse=True)
                print('Warning: More than 2 remaining geometries. Extra geometries:', sorted_geoms[2:])
                # Keep only the largest two geometries
                # remaining_geometries = sorted_geoms[:2]
            return remaining_geometries

    def __get_overlapping_sections(self, section_a: dict) -> list[dict]:
        """
        Finds all sections within self which overlap with the provided section
        and returns them in a list.
        Args:
            section_a (dict): All data pertaining to a section.
        Returns:
            A list of overlap section data, sorted by start_km
        """
        overlapping_sections = []
        for section_b_index, section_b in self.sections.items():
            # First, dismiss all sections which have a non-overlapping range,
            # which prevents the more complex self.__get_overlap() function from being called.
            if self.__determine_range_overlap(section_a['km_range'], section_b['km_range']):

                overlap_geometry = self.__get_overlap(section_a['geometry'], section_b['geometry'])

                if overlap_geometry:
                    overlapping_sections.append({'index': section_b_index,
                                                 'section_info': section_b,
                                                 'geom': overlap_geometry})

        # For the rest of the implementation, this sorting is assumed.
        overlapping_sections = sorted(overlapping_sections, key=lambda x: min(x['section_info']['km_range']))

        return overlapping_sections

    @staticmethod
    def __get_overlap(geometry1: LineString, geometry2: LineString) -> LineString | None:
        """
        Finds the overlap geometry between two Shapely geometries.
        Args:
            geometry1 (LineString): The first Shapely LineString.
            geometry2 (LineString): The second Shapely LineString.
        Returns:
            LineString: The overlap geometry.
            None: If there is no overlap geometry.
        Note:
            The function uses the `intersection` method from Shapely to compute the overlap
            between the two LineString geometries.
            If the geometries do not overlap or have only a point of intersection, the function
            returns an empty LineString.
        """
        overlap_geometry = intersection(geometry1, geometry2, grid_size=1)

        if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
            return line_merge(overlap_geometry)
        elif isinstance(overlap_geometry, LineString) and not overlap_geometry.is_empty:
            return overlap_geometry
        else:
            return None

    def get_sections(self) -> list:
        return [section for section in self.sections.values()]

    def get_properties_at(self, km: float, side: str) -> list[dict]:
        """
        Find the properties of a road section at a specific km.
        Args:
            km (float): Kilometer point to retrieve the road section for.
            side (str): Side of the road to retrieve the road section for.
        Returns:
            list[dict]: Attributes of the road section(s) at the specified kilometer point.
        """
        sections = []
        for section_index, section_info in self.sections.items():
            if section_info['properties']['Baanpositie'] == side:
                if min(section_info['km_range']) <= km <= max(section_info['km_range']):
                    sections.append(section_info['properties'])
        if len(sections) > 1:
            print("Warning: This slice has two roadlines.")
            i = 0
            for section in sections:
                i += 1
                print('Properties at', side, ', side', km, 'km (', i, '):', section)
        else:
            print('Properties at', side, ', side', km, 'km:', sections[0])
        return sections

    def print_section_info(self):
        for section_index, section_info in self.sections.items():
            print("Section", section_index, 'has km-range', section_info['km_range'],
                  'and properties:', section_info['properties'])

    def get_section_info_at(self, km: float, side: str) -> list[dict]:
        section_info = []
        for section_index, section in self.sections.items():
            if section['properties']['Baanpositie'] == side:
                if min(section['km_range']) <= km <= max(section['km_range']):
                    section_info.append(section)
        return section_info


def get_range_diff(range1: list, range2: list, length_estimate: float) -> list:
    """
    Determines the difference between two range elements.
    Args:
        range1 (list): First list indicating a range.
        range2 (list): Second list indicating a range.
        length_estimate (float): Length (estimate) of the object.
    Returns:
        The range that constitutes the difference between the input ranges.
    Example:
        The difference between the range [1, 8] and [5, 8] can be found as [1, 5].
    Note:
        In case there is a symmetric difference, this function will pick the
        range difference with a length closest to the object length provided.
        The assumption is made that the remaining lengths differ. For the
        WEGGEG data, the assumption is likely to hold. An exception will be
        raised if this assumption is broken.
    """
    assert range1 != range2, "Input ranges invalid."

    start1, end1 = sorted(range1)
    start2, end2 = sorted(range2)

    # Find the common part
    common_start = max(start1, start2)
    common_end = min(end1, end2)
    start = min(start1, start2, end1, end2)
    end = max(start1, start2, end1, end2)

    # Find the unique parts
    unique_part_low = [start, common_start]
    unique_part_high = [common_end, end]

    # Find which part's length is closest to the length estimate
    diff1 = abs(length_estimate - get_km_length(unique_part_low))
    diff2 = abs(length_estimate - get_km_length(unique_part_high))

    if diff1 < diff2:
        return unique_part_low
    elif diff2 < diff1:
        return unique_part_high
    else:
        raise Exception("Assumption violated: Remaining lengths are equal and therefore cannot be discerned.")


def get_km_length(km: list) -> int:
    return round(1000*abs(km[1] - km[0]))


def same_direction(geom1: LineString, geom2: LineString) -> bool:
    overlap = shared_paths(geom1, geom2)
    same_direction_overlap = overlap.geoms[0]
    opposite_direction_overlap = overlap.geoms[1]

    print(same_direction_overlap, opposite_direction_overlap)
    assert not all([is_empty(same_direction_overlap), is_empty(opposite_direction_overlap)]), "No overlap at all"

    return is_empty(opposite_direction_overlap)


class MSIRow:
    def __init__(self, name: str, props: dict):
        self.MSIs = []
        self.road_properties = props
        self.name = name

    def define_MSIs(self):
        i_msi = 0
        for msi_numbering in self.road_properties['Rijstrooksignaleringen']:
            self.MSIs[i_msi] = MSI(self.name + str(msi_numbering), msi_numbering, self.road_properties)
            i_msi += 1


class MSI:
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

    def __init__(self, name: str, lane_number: int, props: dict):
        self.displayoptions = self.displayset_all
        self.name = name
        self.lane_number = lane_number
        self.road_properties = props

        self.properties = {
            # 'RSU': None,  # RSU name [Not available]
            'c': None,  # Current MSI
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
            'r': None,  # MSI left
            'l': None,  # MSI left
            'STAT_V': None,  # Static maximum speed
            'DYN_V': None,  # Dynamic maximum speed [?]
            'C_X': None,  # True if continue-X relation [?]
            'C_V': None,  # True if continue-V relation [?]
            'TS': None,  # All MSIs in CW.
            'TS_num': None,  # CW numbering.
            'TS_right': None,  # All MSIs in CW to the right.
            'TS_left': None,  # All MSIs in CW to the left.
            'DIF_V_right': None,  # DIF-V influence from the right [?]
            'DIF_V_left': None,  # DIF-V influence from the left [?]
            'CW': None,  # All MSIs in CW.
            'CW_num': None,  # CW numbering.
            'CW_right': None,  # All MSIs in CW to the right.
            'CW_left': None,  # All MSIs in CW to the left.
            'row': None,  # All MSIs in row.
            'RHL': None,  # True if MSI in RHL.
            'Exit_Entry': None,  # True if MSI in RHL and normal lanes left and right. [?]
            'RHL_neighbor': None,  # True if RHL in row.
            'Hard_shoulder_right': None,  # True if hard shoulder directly to the right.
            'Hard_shoulder_left': None,  # True if hard shoulder directly to the left.
            'N_row': None,  # Number of MSIs in row.
            'N_TS': None,  # Number of MSIs in traffic stream.
            'N_CW': None,  # Number of MSIs in carriageway.
            # 'State': None,  # Active legend. [Not applicable]
        }

    def determine_MSI_relations(self):
        self.properties['c'] = self.name

    def determine_MSI_properties(self):
        self.properties['STAT_V'] = self.road_properties['Maximumsnelheid']

        self.properties['RHL_neighbor'] = 'Spitsstrook' in self.road_properties.items()
        self.properties['RHL'] = self.road_properties[self.lane_number] = 'Spitsstrook'
