import geopandas as gpd
import pandas as pd
from shapely import *
import csv

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
        # "data/Maximum snelheid/max_snelheden.dbf",
        # "data/Convergenties/convergenties.dbf",
        # "data/Divergenties/divergenties.dbf",
        # "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    def __init__(self):
        self.data = {}
        self.extent = None

    def load_data_frames(self, location: str):
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            location (str): The name of the location.
        """
        self.__get_extent(location)
        for file_path in DataFrameLoader.__FILE_PATHS:
            df_layer_name = self.__get_layer_name(file_path)
            self.data[df_layer_name] = self.__load_data_frame(file_path)
            self.__edit_columns(df_layer_name)

    def __load_data_frame(self, file_path: str) -> gpd.GeoDataFrame:
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

        # The geometry column can be rounded
        data['geometry'] = data['geometry'].apply(lambda geom: set_precision(geom, 0.01))

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

        elif df_name == 'Kantstroken':
            data['Vluchtstrook'] = data['OMSCHR'] == 'Vluchtstrook'
            data['Spitsstrook'] = data['OMSCHR'] == 'Spitsstrook'
            data['Puntstuk'] = data['OMSCHR'] == 'Puntstuk'  # TODO: Add support for more options
            data.drop(columns=['OMSCHR'])

        elif df_name == 'Rijstrooksignaleringen':
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
        self.__import_dataframe(dfl, 'Rijstroken')
        self.__import_dataframe(dfl, 'Kantstroken')
        # self.__import_dataframe(dfl, 'Maximum snelheid')

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str):
        """
        Load road sections and attributes from a DataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
        """
        # print('Currently importing', df_name, '...')
        if df_name == 'Rijstroken':
            columns_of_interest = ['nLanes']
        elif df_name == 'Kantstroken':
            columns_of_interest = ['Vluchtstrook', 'Spitsstrook', 'Puntstuk']
        elif df_name == 'Maximum snelheid':
            columns_of_interest = ['OMSCHR']
        else:
            columns_of_interest = []

        # TODO: First import can be made simpler, by ignoring overlap (as long as there is no inter-layer overlap)

        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            section_info = self.__extract_row_properties(row, columns_of_interest)

            print("")
            print("Now adding section", self.section_index, ":", section_info['side'],
                  section_info['km_range'], section_info['properties'], section_info['geometry'])

            self.__determine_sectioning(section_info)

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
        Determine how to merge new section to existing sections.
        Args:
            new_section (dict): All relevant information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            # No overlap with other sections. Add section regularly
            print("This is a new section without overlap.")
            self.__add_section(new_section)
        else:
            # Loop over all overlap instances.
            while len(overlap_sections) > 0:
                print("Number of overlapping sections:", len(overlap_sections))
                # Extract relevant overlap properties of the first item and remove it from the list
                overlap_geometry = overlap_sections[0]['geom']
                other_section = overlap_sections[0]['section_info']
                other_section_index = overlap_sections[0]['index']
                overlap_sections.pop(0)

                print('New section geom:', new_section['geometry'])
                print('Other section geom:', other_section['geometry'])
                print('Overlap geom:', overlap_geometry) # TODO: make this in the same shape

                assert new_section['side'] == other_section['side'], "The overlap is not on the same side of the road."

                # Set has only unique values
                registration_points = sorted({new_section['km_range'][0], new_section['km_range'][1],
                                              other_section['km_range'][0], other_section['km_range'][1]})
                # print(registration_points).

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
                # - Add overlapping section (by updating the original other_section)
                #   - Determine start and end of section
                #   - Apply both properties
                #   - Reduce geometry size
                # - Add new section (by deriving the remainder)
                #   - Determine start and end of remainder section
                #   - Select property of remainder section
                #   - Increase index
                elif len(registration_points) == 3:
                    remaining_geometry = self.__get_remainder(new_section['geometry'], other_section['geometry'])

                    print('Remaining geom:', remaining_geometry)

                    # Check that there is a non-empty valid remaining geometry.
                    assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                    assert isinstance(remaining_geometry, LineString), 'Remaining part is not a LineString.'

                    print('Found equal geometries with equal start OR end. Determining sections...')

                    # Update other section
                    midpoint = registration_points[1]

                    if new_section['km_range'][0] == other_section['km_range'][0]:
                        km_range = [midpoint, new_section['km_range'][0]]
                    elif new_section['km_range'][1] == other_section['km_range'][1]:
                        km_range = [midpoint, new_section['km_range'][0]]

                    self.__update_section(other_section_index, km_range, new_section['properties'], overlap_geometry)

                    # Create new section
                    remainder_properties = {}

                    # Determine relevant registration point
                    if new_section['km_range'][0] == other_section['km_range'][0]:
                        used_points = [midpoint, new_section['km_range'][0]]
                    elif new_section['km_range'][1] == other_section['km_range'][1]:
                        used_points = [midpoint, new_section['km_range'][1]]
                    remainder_rp = [point for point in registration_points if point not in used_points][0]

                    if remainder_rp == new_section['km_range'][0] or remainder_rp == new_section['km_range'][1]:
                        remainder_properties = new_section['properties']
                    elif remainder_rp == other_section['km_range'][0] or remainder_rp == other_section['km_range'][1]:
                        remainder_properties = other_section['properties']

                    remainder_section = {
                        'side': new_section['side'],
                        'km_range': [remainder_rp, midpoint],
                        'properties': remainder_properties,
                        'geometry': remaining_geometry
                    }
                    self.__add_section(remainder_section)

                # 0/2 equal case, with 3 resulting sections. 4 possible combinations
                # Desired behaviour:
                # - Determine appropriate problem splitting TODO: change code to do this.
                elif len(registration_points) == 4:
                    remaining_geometry = other_section['geometry'].symmetric_difference(new_section['geometry'])

                    print('Remaining geom:', remaining_geometry)
                    # print(get_num_geometries(remaining_geometry))

                    # Check that there is a non-empty remaining geometry.
                    assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                    assert isinstance(remaining_geometry, MultiLineString), 'Incorrect remaining geometry'

                    print('Found partly overlapping geometries. Determining problem splitting...')

                    # Overlapping section
                    logpoints = [new_section['km_range'][0], new_section['km_range'][1],
                                 other_section['km_range'][0], other_section['km_range'][1]]
                    logpoints.sort()

                    self.__update_section(other_section_index, logpoints[1:3],
                                          new_section['properties'], overlap_geometry)

                    # Create new sections
                    remainder_geometries = [geom for geom in remaining_geometry.geoms]
                    assert len(remainder_geometries) == 2, 'There are too many remaining geometries in the geom below.'
                    for i in [0, 1]:
                        remainder_properties = {}
                        new_overlap = self.__get_overlap(remainder_geometries[i], new_section['geometry'])
                        other_overlap = self.__get_overlap(remainder_geometries[i], other_section['geometry'])
                        if not new_overlap.is_empty:
                            remainder_properties = new_section['properties']
                        elif not other_overlap.is_empty:
                            remainder_properties = other_section['properties']
                        else:
                            raise Exception('Something went wrong.')

                        remainder_section = {
                            'side': new_section['side'],
                            'km_range': [logpoints[i*2], logpoints[i*2+1]],
                            'properties': remainder_properties,
                            'geometry': remainder_geometries[i]
                        }
                        self.__add_section(remainder_section)

    @staticmethod
    def __determine_range_overlap(range1: list, range2: list) -> bool:
        """
        Determines whether there is overlap between two ranges.
        Args:
            range1 (list): First range with two float values.
            range2 (list): Second raneg with float values.
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
            km_range (list[float]): Start and end registration kilometre.
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
                - km_range (list[float]): Start and end registration kilometre.
                - properties (dict): All properties that belong to the section.
                - geometry (LineString): The geometry of the section.
        Prints:
            Newly added section properties to log window.
        """
        self.sections[self.section_index] = new_section
        self.__log_section(self.section_index)
        self.section_index += 1

    def __log_section(self, index: int):
        print("Added a new section at index", index, "with:",
              self.sections[index]['side'],
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    def __log_section_change(self, index: int):
        print("Adjusted the properties of section", index, "to:",
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
        remaining_geometry = section1.difference(section2)

        # If empty, try the other way around.
        if is_empty(remaining_geometry):
            remaining_geometry = section2.difference(section1)

        return remaining_geometry

    def __get_overlapping_sections(self, section_a: dict) -> list[dict]:
        overlapping_sections = []
        for section_b_index, section_b in self.sections.items():
            # First, dismiss all sections which have a completely different begin and end range,
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
            between the two geometries.
            If the geometries do not overlap or have only a point of intersection, the function
            returns an empty LineString and False.
        """
        overlap_geometry = intersection(geometry1, geometry2)

        if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
            return line_merge(overlap_geometry)
        elif isinstance(overlap_geometry, LineString) and not overlap_geometry.is_empty:
            return overlap_geometry
        else:
            return LineString([])

    def get_properties_at(self, km: float, side: str) -> dict:
        """
        Find the properties of a road section at a specific km.
        Args:
            km (float): Kilometer point to retrieve the road section for.
            side (str): Side of the road to retrieve the road section for.
        Returns:
            dict: Attributes of the road section at the specified kilometer point.
        """
        sections = []
        for section_index, section_info in self.sections.items():
            if section_info['side'] == side:
                if min(section_info['km_range']) <= km <= max(section_info['km_range']):
                    sections.append(section_info['properties'])
        if len(sections) > 1:
            print("Warning: This slice has two roadlines.")
        print(sections)
        return sections
