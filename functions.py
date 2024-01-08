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

        if name == 'Rijstrooksignaleringen':
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            is_kp = self.data[name]['CODE'] == 'KP'
            self.data[name] = self.data[name][is_kp]

        # These general columns are not further necessary.
        # self.data[df_name].drop(columns=['FK_VELD4', 'IBN', 'inextent'], inplace=True)

        # All 'stroken' dataframes have VNRWOL columns which should be converted to integer.
        # if 'stroken' in name:
        #     self.data[name]['VNRWOL'] = pd.to_numeric(self.data[name]['VNRWOL'], errors='coerce').astype('Int64')

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

    @staticmethod
    def __extract_row_properties(row: pd.Series, name: str):
        """
        Turns the contents of a road data Dataframe row into a dictionary with the relevant entries.
        Args:
            row (pd.Series): Row containing information about the road section
            name (str): Name of dataframe.
        """
        if name == 'Rijstroken':
            properties = {
                'Baanpositie': row['IZI_SIDE'],
                'nRijstroken': row['nRijstroken'],
                'Wegnummer': row['WEGNUMMER']
                # 'Volgnummer': row['VOLGNRWOL']
            }

        if name == 'Kantstroken':
            properties = {
                'Vluchtstrook': row['OMSCHR'] == 'Vluchtstrook',
                'Spitsstrook': row['OMSCHR'] == 'Spitsstrook',
                'Puntstuk': row['OMSCHR'] == 'Puntstuk',
                'RedresseerstrookL': (row['OMSCHR'] == 'Redresseerstrook') &
                                     (row['IZI_SIDE'] == 'L'),
                'RedresseerstrookR': (row['OMSCHR'] == 'Redresseerstrook') &
                                     (row['IZI_SIDE'] == 'R'),
                'Bufferstrook': row['OMSCHR'] == 'Bufferstrook',
                'Plusstrook': row['OMSCHR'] == 'Plusstrook',
            }

        if name == 'Maximum snelheid':
            properties = {
                'Snelheid': row['OMSCHR']
            }

        if name == 'Rijstrooksignaleringen':
            properties = {
                'Rijstroken': [int(char) for char in row['RIJSTRKNRS']],
                'km': row['KMTR']
            }

        if row['KANTCODE'] == 'T':
            geom = reverse(row['geometry'])
        elif row['KANTCODE'] == 'H':
            geom = row['geometry']
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

        # while get_num_coordinates(new_section_geom) != 0:
        for overlap_section in overlap_sections:
            overlap_index = overlap_section['index']
            overlap_section = deepcopy(overlap_section['section_info'])
            overlap_geom = overlap_section['geometry']

            other_section_range = overlap_section['km_range']
            other_section_props = overlap_section['properties']
            other_section_geom = overlap_section['geometry']

            # TODO: Assert that there is also some overlap in the km?
            assert self.__determine_range_overlap(new_section_range, other_section_range)

            # Case 1: start is equal
            if min(new_section_range) == min(other_section_range):
                if max(new_section_range) == max(other_section_range):
                    assert new_section_geom.equals(other_section_geom), 'Inconsistent geometries.'
                    self.__update_section(overlap_index, props=new_section_props)
                    continue
                if max(new_section_range) < max(other_section_range):
                    # other_section aanpassen
                    # ...
                    continue
                if max(new_section_range) > max(other_section_range):
                    self.__update_section(overlap_index, props=new_section_props)
                    # Trim the new_section range and geometry for another go.
                    new_section_range = [max(other_section_range), max(new_section_range)]
                    new_section_geom = self.__get_remainder(new_section_geom, other_section_geom)[0]
                    continue

            # Case 2: new_section starts earlier.
            # Add section between new_section_start and other_section_start
            # with new_section properties and geometry
            if min(new_section_range) < min(other_section_range):
                added_geom = self.__get_remainder(new_section_geom, other_section_geom)[0]
                self.__add_section({
                    'km_range': sorted([min(new_section_range), min(other_section_range)]),
                    'properties': new_section_props,
                    'geometry': added_geom
                })
                # Trim the new_section range and geometry for another go.
                new_section_range = [min(other_section_range), max(new_section_range)]
                new_section_geom = self.__get_remainder(added_geom, other_section_geom)

            # Case 3: new_section starts later
            if min(new_section_range) > min(other_section_range):
                # Add section between new_section_start and other_section_start with other_section properties
                print('ha')

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
                if not o.is_empty:
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
        """
        min1, max1 = min(range1), max(range1)
        min2, max2 = min(range2), max(range2)
        overlap = max(min1, min2) <= min(max1, max2)
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
        if km_range:
            self.sections[index]['km_range'] = sorted(km_range)
        if props:
            self.sections[index]['properties'].update(props)
        if geom:
            self.sections[index]['geometry'] = geom
        # self.__log_section_change(index)

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
        self.sections[self.section_index] = new_section
        self.__log_section(self.section_index)
        self.section_index += 1

    def __log_section(self, index: int):
        print("[LOG:] Section", index, "added:",
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    def __log_section_change(self, index: int):
        print("[LOG:] Section", index, "changed:",
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

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

        print(f"Warning: Empty remaining geometry: {remaining_geometry}")

        if isinstance(remaining_geometry, LineString):
            return [remaining_geometry]

        if isinstance(remaining_geometry, MultiLineString):
            remaining_geometries = [geom for geom in remaining_geometry.geoms]
            if get_num_geometries(remaining_geometry) > 2:
                sorted_geoms = sorted(remaining_geometries, key=lambda geom: geom.length, reverse=True)
                # Keep only the largest two geometries
                remaining_geometries = sorted_geoms[:2]
                print('Warning: More than 2 remaining geometries. Removed', sorted_geoms[2:])
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

                if not overlap_geometry.is_empty:
                    overlapping_sections.append({'index': section_b_index,
                                                 'section_info': section_b,
                                                 'geom': overlap_geometry})

        # For the rest of the implementation, this sorting is assumed.
        overlapping_sections = sorted(overlapping_sections, key=lambda x: min(x['section_info']['km_range']))

        return overlapping_sections

    @staticmethod
    def __get_overlap(geometry1: LineString, geometry2: LineString) -> LineString:
        """
        Finds the overlap geometry between two Shapely geometries.
        Args:
            geometry1 (LineString): The first Shapely LineString.
            geometry2 (LineString): The second Shapely LineString.
        Returns:
            LineString: The overlap geometry (or an empty LineString).
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
            return LineString([])

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


def get_middle_value(input_set: set) -> any:
    """
    Find the middle value of a set of three number values.
    Args:
        input_set (set): Set with three number values.
    Returns:
        Middle value of set.
    """
    assert len(input_set) == 3, 'Incorrect set length.'
    sorted_set = sorted(input_set)
    return sorted_set[1]


def process_registration_points(rp1: list, rp2: list) -> (int, int, list[int], int):
    """
    Determines point properties based on the two given lists of registration points.
    The assumption is made that two of the four points overlap.
    Args:
        rp1 (list): First list of registration points.
        rp2 (list): Second list of registration points.
    Returns:
        The value of the midpoint of the three remaining registration points.
        The value of the overlapping point between the two lists.
        The unique points of the two lists, sorted.
        The extreme point: the unique point which is not the midpoint.
    """
    s1 = set(rp1)
    s2 = set(rp2)
    all_points = s1 | s2
    assert len(all_points) == 3, "Assumption violated."

    midpoint = get_middle_value(all_points)
    overlapping_point = s1.intersection(s2)
    unique_points = s1.symmetric_difference(s2)
    extreme_point = unique_points.symmetric_difference({midpoint})
    return midpoint, overlapping_point.pop(), sorted(unique_points), extreme_point.pop()


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
