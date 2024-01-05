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
        Select data in the specified extent from the GeoDataFrame.
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with only data inside the extent.
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

    def __edit_columns(self, df_name: str):
        """
        Edit columns from the GeoDataFrame.
        Args:
            df_name (str): The name of the GeoDataFrame.
        """
        data = self.data[df_name]

        # The geometry column can be rounded (use 0.01 for cm or 1 for meter precision)
        data['geometry'] = data['geometry'].apply(lambda geom: set_precision(geom, 1))

        # These columns are not necessary in this project.
        data.drop(columns=['FK_VELD4', 'IBN', 'inextent'], inplace=True)

        # These column variable types should be changed.
        data['WEGNUMMER'] = pd.to_numeric(data['WEGNUMMER'], errors='coerce').astype('Int64')

        # All 'stroken' dataframes have VNRWOL columns which should be converted to integer
        if 'stroken' in df_name:
            data['VNRWOL'] = pd.to_numeric(data['VNRWOL'], errors='coerce').astype('Int64')

        # More specific data edits
        if df_name == 'Rijstroken':
            lane_mapping = {'1 -> 1': 1, '2 -> 2': 2, '3 -> 3': 3, '4 -> 4': 4, '5 -> 5': 5}
            data['nLanes'] = data['OMSCHR'].apply(lambda df: lane_mapping.get(df, df))
            data.drop(columns=['OMSCHR'])

            # VOLGNRSTRK to integer, supporting NaN values
            data['VOLGNRSTRK'] = (pd.to_numeric(data['VOLGNRSTRK'], errors='coerce').astype('Int64'))

        if df_name == 'Kantstroken':
            data['Vluchtstrook'] = data['OMSCHR'] == 'Vluchtstrook'
            data['Spitsstrook'] = data['OMSCHR'] == 'Spitsstrook'
            data['Puntstuk'] = data['OMSCHR'] == 'Puntstuk'  # TODO: Add support for more options
            data.drop(columns=['OMSCHR'])

        if df_name == 'Rijstrooksignaleringen':
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            data = data[data['CODE'] == 'KP']

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

    def import_dataframes(self, dfl: DataFrameLoader):
        """
        Load road attributes from all DataFrames.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
        """
        self.__import_first_dataframe(dfl, 'Rijstroken', ['nLanes'])
        self.__import_dataframe(dfl, 'Kantstroken', ['Vluchtstrook', 'Spitsstrook', 'Puntstuk'])
        self.__import_dataframe(dfl, 'Maximum snelheid', ['OMSCHR'])

    def __import_first_dataframe(self, dfl: DataFrameLoader, df_name: str, columns_of_interest: list[str]):
        """
        Load road sections and attributes from the first DataFrame, without checking for overlap.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
            columns_of_interest (list): Names of dataframe columns to be imported.
        Note:
            There is no overlap check! Ensure that there is no overlap within the layer itself.
        """
        print('>>> [STATUS:] Importing', df_name, '...')
        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            section_info = self.__extract_row_properties(row, columns_of_interest)
            self.__add_section(section_info)

        # self.print_section_info()
        print('>>> [STATUS:] Added', self.section_index, 'sections. '
              'The model has', self.section_index, 'sections in total.')

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str, columns_of_interest: list[str]):
        """
        Load road sections and attributes from a DataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
            columns_of_interest (list): Names of dataframe columns to be imported.
        """
        print("")
        print('>>> [STATUS:] Importing', df_name, '...')
        current_sections = self.section_index

        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            section_info = self.__extract_row_properties(row, columns_of_interest)
            self.__determine_sectioning(section_info)

        # self.print_section_info()
        print('>>> [STATUS:] Added', self.section_index-current_sections, 'sections. '
              'The model has', self.section_index, 'sections in total.')

    @staticmethod
    def __extract_row_properties(row: pd.Series, columns_of_interest: list[str]):
        """
        Turns the contents of a road data Dataframe row into a dictionary with the relevant entries.
        Args:
            row (pd.Series): Row containing information about the road section
            columns_of_interest (list[str]): List of column names from Dataframe to be extracted.
        """
        return {'side': row['IZI_SIDE'],
                'km_range': [row['BEGINKM'], row['EINDKM']],
                'properties': row[columns_of_interest].to_dict(),
                'geometry': row['geometry']}

    def __determine_sectioning(self, new_section: dict):
        """
        Determine how to merge provided section with existing sections.
        Args:
            new_section (dict): All relevant information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            # print("This is a new section without overlap.")
            self.__add_section(new_section)
            return

        # Loop over all overlapping sections.
        # print("Number of overlapping sections to handle:", len(overlap_sections))
        for overlap_section in overlap_sections:
            # Extract relevant overlap properties
            other_section_index = overlap_section['index']
            other_section = deepcopy(overlap_section['section_info'])  # Deepcopy prevents aliasing
            overlap_geometry = deepcopy(overlap_section['geom'])

            assert new_section['side'] == other_section['side'], "The overlap is not on the same side of the road."

            # Determine all km registration points
            registration_points = set(new_section['km_range']) | set(other_section['km_range'])
            # print('Registration points:', registration_points)
            # print('This could generate', len(registration_points) - 1, 'section(s).')

            # Fully equal case, with 1 resulting section. 1 possible combination.
            # Desired behaviour:
            # - Add new_section's property to original entry.
            # - Change nothing else.
            if len(registration_points) == 2:
                assert new_section['geometry'].equals(other_section['geometry']), 'Inconsistent geometries.'
                print('Found equal geometries with equal start and end. Combining the properties...')
                self.__update_section(other_section_index, props=new_section['properties'])

            # 1/2 equal case, with 2 resulting sections. 4 possible combinations.
            # Desired behaviour:
            # - Determine start and end of sections.
            # - Add new section (by deriving the remainder)
            #   - Select property of remainder section
            #   - Add section, increase index
            # - Update overlapping section (by adjusting the original other_section)
            #   - Update with new_section properties
            #   - Update geometry to overlapping part
            elif len(registration_points) == 3:
                remaining_geometry = self.__get_remainder(new_section['geometry'], other_section['geometry'])

                # Check that there is a non-empty valid remaining geometry.
                assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                assert isinstance(remaining_geometry, LineString), 'Remaining part is not a LineString.'

                print('Found equal geometries with equal start OR end. Determining sections...')

                # Determine new section registration points
                midpoint, overlapping_point, unique_points, extreme_point = (
                    process_registration_points(new_section['km_range'], other_section['km_range']))

                # Determine new section properties
                if extreme_point in new_section['km_range']:
                    remainder_properties = new_section['properties']
                elif extreme_point in other_section['km_range']:
                    remainder_properties = other_section['properties']
                else:
                    raise Exception("No match found for extreme registration point.")

                # Add new section
                self.__add_section({
                    'side': new_section['side'],
                    'km_range': sorted(unique_points),
                    'properties': remainder_properties,
                    'geometry': remaining_geometry
                })

                # Update other_section
                self.__update_section(index=other_section_index,
                                      km_range=[midpoint, overlapping_point],
                                      props=new_section['properties'],
                                      geom=overlap_geometry)

            # 0/2 equal case, with 3 resulting sections. 4 possible combinations
            # Desired behaviour:
            # - Determine registration points
            # - Determine geometries
            # - Add 2 new sections with the appropriate properties
            # - Update overlapping section (by adjusting the original other_section)
            #   - Update with new_section properties
            #   - Update geometry to overlapping part
            elif len(registration_points) == 4:
                print('boo:', registration_points)
                # print(new_section['km_range'], other_section['km_range'])

                remaining_geometry = symmetric_difference(new_section['geometry'],
                                                          other_section['geometry'],
                                                          grid_size=1)
                print('new', new_section['geometry'])
                print('other', other_section['geometry'])
                print('remaining:', remaining_geometry)

                # Check that there is a non-empty remaining geometry.
                assert isinstance(remaining_geometry, MultiLineString), 'Incorrect remaining geometry'
                assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'

                print('Found partly overlapping geometries. Determining sections...')

                # Determine relevant remainder geometries
                remainder_geometries = [geom for geom in remaining_geometry.geoms]
                if get_num_geometries(remaining_geometry) > 2:
                    sorted_geometries = sorted(remainder_geometries, key=lambda geom: geom.length, reverse=True)
                    # Keep only the largest two geometries
                    remainder_geometries = sorted_geometries[:2]
                    # print('Warning: More than 2 remaining geometries. Removed', sorted_geometries[2:])

                # Create new section(s)
                taken_points = []
                for i in [0, 1]:
                    print(remainder_geometries[i])
                    # Check if remainder overlaps another overlap section. If so, then we will NOT add a new section.
                    any_other_overlap = False
                    for other_overlap in overlap_sections:
                        if other_overlap['geom'] != overlap_geometry:
                            o = self.__get_overlap(remainder_geometries[i], other_overlap['geom'])
                            if not o.is_empty:
                                any_other_overlap = True
                                break

                    if not any_other_overlap:
                        # Determine registration points
                        if taken_points:
                            remainder_points = sorted(set(registration_points).symmetric_difference(set(taken_points)))
                            print('we have already used', taken_points, ', so now we use', remainder_points)
                        else:
                            # Determine which geometry this remainder is part of
                            new_overlap = self.__get_overlap(remainder_geometries[i], new_section['geometry'])
                            other_overlap = self.__get_overlap(remainder_geometries[i], other_section['geometry'])
                            assert sum(
                                [new_overlap.is_empty, other_overlap.is_empty]) == 1, "Overlap situation unclear."

                            # Determine properties of the geometry
                            if other_overlap.is_empty and not new_overlap.is_empty:
                                remainder_properties = new_section['properties']
                                section_points = new_section['km_range']
                                other_points = other_section['km_range']
                            elif new_overlap.is_empty and not other_overlap.is_empty:
                                remainder_properties = other_section['properties']
                                section_points = other_section['km_range']
                                other_points = new_section['km_range']
                            else:
                                raise Exception('Something went wrong.')

                            print('Section points:', section_points, 'Other points:', other_points)
                            print('Reg points:', sorted(registration_points))

                            remainder_length = remainder_geometries[i].length

                            remainder_points = get_range_diff(section_points, other_points, remainder_length)

                            taken_points = remainder_points

                        print('Lengths:', remainder_length, get_km_length(taken_points))
                        print('taken poitns:', taken_points)

                        self.__add_section({
                            'side': new_section['side'],
                            'km_range': remainder_points,
                            'properties': remainder_properties,
                            'geometry': remainder_geometries[i]
                        })

                # Update overlapping section
                self.__update_section(other_section_index, sorted(registration_points)[1:3],
                                      new_section['properties'], overlap_geometry)

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
        self.__log_section_change(index)

    def __add_section(self, new_section: dict):
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict): Containing:
                - side (str): Side of the road ('L' or 'R').
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
        print("[LOG:] Added a new section at index", index, "with:",
              self.sections[index]['side'],
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    def __log_section_change(self, index: int):
        print("[LOG:] Adjusted the properties of section", index, "to:",
              self.sections[index]['side'],
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    @staticmethod
    def __get_remainder(section1, section2) -> LineString:
        """
        Finds the geometry that two Shapely LineStrings do NOT have in common.
        Args:
            section1 (LineString): The first Shapely LineString.
            section2 (LineString): The second Shapely LineString.
        Returns:
            LineString describing the geometry that is the difference between the two provided sections.
        """
        remaining_geometry = difference(section1, section2, grid_size=1)

        # If empty, try the other way around.
        if is_empty(remaining_geometry):
            remaining_geometry = difference(section2, section1, grid_size=1)

        # Determine relevant remainder geometries
        if isinstance(remaining_geometry, MultiLineString):
            # Keep only the largest geometry. Other geometries are tiny remainder lines
            # caused by rounding errors elsewhere. These are hereby ignored.
            remainder_geometries = [geom for geom in remaining_geometry.geoms]
            sorted_geometries = sorted(remainder_geometries, key=lambda geom: geom.length, reverse=True)
            remaining_geometry = sorted_geometries[0]
            # print('Warning: More than 1 remaining geometry. Removed', sorted_geometries[1:])

        return remaining_geometry

    def __get_overlapping_sections(self, section_a: dict) -> list[dict]:
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
            if section_info['side'] == side:
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
            if section['side'] == side:
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


def get_range_diff(range1: list, range2: list, length: float) -> list:
    """
    Determines the difference between two range elements.
    Args:
        range1 (list): First list indicating a range.
        range2 (list): Second list indicating a range.
        length (float): Length (estimate) of the object.
    Returns:
        The range that constitutes the difference between the input ranges.
    Example:
        The difference between the range [1, 8] and [5, 8] can be found as [1, 5].
    Note:
        In case there is a symmetric difference, this function will pick the
        range difference with a length closest to the object length provided.
    """
    print('Ranges', range1, range2)
    assert range1 != range2, "Input not good"

    start1, end1 = sorted(range1)
    start2, end2 = sorted(range2)

    # Find the common part
    common_start = max(start1, start2)
    common_end = min(end1, end2)
    start = min(start1, start2, end1, end2) # this introduces another problem case
    end = max(start1, start2, end1, end2)

    unique_part_low = [start, common_start]
    unique_part_high = [common_end, end]

    print('unique parts', unique_part_low, unique_part_high)
    assert unique_part_low != unique_part_high, "Something went wrong"

    unique_part_low_length = get_km_length(unique_part_low)
    unique_part_high_length = get_km_length(unique_part_high)

    print(length, unique_part_high_length, unique_part_low_length)

    # Find which length is closest to 'length'
    diff1 = abs(length - unique_part_low_length)
    diff2 = abs(length - unique_part_high_length)

    print(diff1, diff2)

    if diff1 < diff2:
        return unique_part_low
    elif diff2 < diff1:
        return unique_part_high
    else:
        raise Exception("Lengths are equal and therefore cannot be discerned.")


def get_km_length(km: list) -> int:
    return round(1000*abs(km[1] - km[0]))
