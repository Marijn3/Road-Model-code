import geopandas as gpd
import pandas as pd
import shapely.geometry
from shapely.geometry import box
import csv

pd.set_option('display.max_columns', None)


class DataFrameLoader:
    """
   A class for loading GeoDataFrames from shapefiles based on a specified location extent.

   Attributes:
       __LOCATIONS_CSV_PATH (str): The file path for the locations csv file.
       __FILE_PATHS (list): List of file paths for shapefiles to be loaded.
       data (dict): Dictionary to store GeoDataFrames for each layer.
       extent (shapely.geometry.box): The extent of the specified location.
   """

    __LOCATIONS_CSV_PATH = 'data/locations.csv'

    # List all data layer files to be loaded.
    __FILE_PATHS = [
        # "data/Convergenties/convergenties.dbf",
        # "data/Divergenties/divergenties.dbf",
        # "data/Rijstrooksignaleringen/strksignaleringn.dbf",
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        # "data/Mengstroken/mengstroken.dbf",
        # "data/Maximum snelheid/max_snelheden.dbf",
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

    def __get_extent(self, location: str) -> shapely.box:
        """
        Determine the extent box of the specified location from coordinates.
        Args:
            location (str): The name of the location.
        Raises:
            ValueError: If the specified location is not found in the csv file.
        """
        coords = self.__load_extent_from_csv(location)

        if coords:
            self.extent = box(minx=coords["west"], miny=coords["south"], maxx=coords["east"], maxy=coords["north"])
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

        # The geometry column can be rounded TODO: Find why it does not work.
        data['geometry'] = data['geometry'].apply(lambda geom: shapely.set_precision(geom, 0.01))

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

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str):
        """
        Load road sections and attributes from a DataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
        """
        print('Currently importing', df_name, '...')
        if df_name == 'Rijstroken':
            columns_of_interest = ['nLanes']
        elif df_name == 'Kantstroken':
            columns_of_interest = ['Vluchtstrook', 'Spitsstrook', 'Puntstuk']
        else:
            columns_of_interest = []

        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            self.__add_section(row, columns_of_interest)

    def __add_section(self, row: pd.Series, columns_of_interest: list[str]):
        """
        Add a road section between start_km and end_km and apply properties.
        Args:
            row (pd.Series): A row from a dataframe.
            columns_of_interest (list[str]): list of column names to be extracted
        """
        # print("Now adding section", self.section_index)

        new_section_side = row['IZI_SIDE']
        new_section_begin = row['BEGINKM']
        new_section_end = row['EINDKM']
        new_section_properties = row[columns_of_interest].to_dict()
        new_section_geometry = row['geometry']
        new_section_geometry = row['geometry']

        # Method to handle propagating properties with intersecting sections.
        overlap_present = False
        overlapping_sections = []
        for other_section_index, other_section in self.sections.items():
            # TODO: First, dismiss all sections which have a completely different begin and end range. THIS SAVES TIME.

            overlap_geometry, overlap_present = self.__check_overlap(new_section_geometry, other_section['geometry'])

            if overlap_present:
                overlapping_sections.append({'geom': overlap_geometry,
                                             'section': other_section,
                                             'index': other_section_index})
                break

        if len(overlapping_sections) == 0:
            # No overlap with other sections. Add section regularly
            self.sections[self.section_index] = {'side': new_section_side,
                                                 'start_km': new_section_begin,
                                                 'end_km': new_section_end,
                                                 'properties': new_section_properties,
                                                 'geometry': new_section_geometry}
            self.section_index += 1
        else:
            # Loop over all overlap instances.
            while len(overlapping_sections) > 0:

                # Extract relevant overlap properties and remove it from the list
                overlap_geometry = overlapping_sections[0]['geom']
                other_section = overlapping_sections[0]['section']
                other_section_index = overlapping_sections[0]['index']
                overlapping_sections.pop(0)

                other_section_side = other_section['side']
                other_section_begin = other_section['start_km']
                other_section_end = other_section['end_km']
                other_section_properties = other_section['properties']
                other_section_geometry = other_section['geometry']

                print('---')
                print('New section geom:', row['geometry'])
                print('Other section geom:', other_section_geometry)
                print('Overlap geom:', overlap_geometry)

                assert new_section_side == other_section_side, "Overlap not on the same side of the road."

                # Determine what kind of overlap it is and thus what should be done to resolve it.
                if other_section_begin == new_section_begin or other_section_end == new_section_end:
                    # Fully equal case, with 1 resulting section. 1 possible combination.
                    if other_section_begin == new_section_begin and other_section_end == new_section_end:
                        #print('Found equal geometries with equal start and end. Combining the properties...')

                        # Check that indeed both geometries are the same, otherwise crash.
                        assert new_section_geometry == other_section_geometry, 'Inconsistent equal geometries.'

                        # Desired behaviour:
                        # - Add new_section's property to original entry.
                        # - Change nothing else.

                        self.sections[other_section_index]['properties'].update(new_section_properties)

                    # 1/2 equal case, with 2 resulting sections. 4 possible combinations.
                    else:
                        #print('Found equal geometries with equal start OR end. Determining sections...')

                        remaining_geometry = other_section_geometry.symmetric_difference(new_section_geometry)
                        print('Remaining geometry:', remaining_geometry)
                        # Check that there is a non-empty remaining geometry.
                        assert shapely.get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                        assert shapely.get_num_geometries(remaining_geometry) == 1, 'Remaining geometry has multiple geometries.'

                        # Desired behaviour:
                        # - Add overlapping section (by updating the original other_section)
                        #   - Determine start and end of section
                        #   - Apply both properties
                        #   - Reduce geometry size

                        if new_section_begin == other_section_begin:
                            midpoint = min(new_section_end, other_section_end)
                            self.sections[other_section_index]['end_km'] = midpoint
                        elif new_section_end == other_section_end:
                            midpoint = max(new_section_begin, other_section_begin)
                            self.sections[other_section_index]['start_km'] = midpoint

                        self.sections[other_section_index]['properties'].update(new_section_properties)

                        self.sections[other_section_index]['geometry'] = overlap_geometry

                        # Desired behaviour:
                        # - Add new section (by deriving the remainder)
                        #   - Determine start and end of remainder section
                        #   - Select property of remainder section
                        #   - Increase index

                        remainder_properties = {}

                        if new_section_begin == other_section_begin:
                            remainder_begin = min(new_section_end, other_section_end)
                            remainder_end = max(new_section_end, other_section_end)
                            if new_section_end < other_section_end:
                                remainder_properties = other_section_properties
                            else:
                                remainder_properties = new_section_properties
                        if new_section_end == other_section_end:
                            remainder_begin = min(new_section_begin, other_section_begin)
                            remainder_end = max(new_section_begin, other_section_begin)
                            if new_section_begin < other_section_begin:
                                remainder_properties = new_section_properties
                            else:
                                remainder_properties = other_section_properties

                        self.sections[self.section_index] = {'side': new_section_side,
                                                             'start_km': remainder_begin,
                                                             'end_km': remainder_end,
                                                             'properties': remainder_properties,
                                                             'geometry': remaining_geometry}

                        self.section_index += 1

                # 0/2 equal case, with 3 resulting sections. 4 possible combinations
                else:
                    # print('Found partly overlapping geometries. Determining sections...')

                    remaining_geometry = other_section_geometry.symmetric_difference(new_section_geometry)

                    # Check that there is a non-empty remaining geometry.
                    assert shapely.get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                    assert isinstance(remaining_geometry, shapely.MultiLineString), 'Incorrect remaining geometry'

                    # Desired behaviour:
                    # - Add overlapping section (by updating the original other_section)
                    #   - Determine start and end of middle section
                    #   - Apply both properties
                    #   - Reduce geometry size

                    logpoints = [new_section_begin, new_section_end, other_section_begin, other_section_end]
                    logpoints.sort()

                    self.sections[other_section_index]['start_km'] = logpoints[1]
                    self.sections[other_section_index]['end_km'] = logpoints[2]
                    self.sections[other_section_index]['properties'].update(new_section_properties)
                    self.sections[other_section_index]['geometry'] = overlap_geometry

                    # Desired behaviour:
                    # - Add new sections (by deriving the remainders)
                    #   - Determine start and end of remainder sections
                    #   - Select property of remainder sections
                    #   - Increase index

                    remaining_geometries = [geom for geom in remaining_geometry.geoms]

                    # First, the left section:
                    if new_section_begin < other_section_begin:
                        remainder_properties = new_section_properties
                    else:
                        remainder_properties = other_section_properties

                    self.sections[self.section_index] = {'side': new_section_side,
                                                         'start_km': logpoints[0],
                                                         'end_km': logpoints[1],
                                                         'properties': remainder_properties,
                                                         'geometry': remaining_geometries[0]}

                    self.section_index += 1

                    # Then, the right section:
                    if new_section_end < other_section_end:
                        remainder_properties = other_section_properties
                    else:
                        remainder_properties = new_section_properties

                    self.sections[self.section_index] = {'side': new_section_side,
                                                         'start_km': logpoints[2],
                                                         'end_km': logpoints[3],
                                                         'properties': remainder_properties,
                                                         'geometry': remaining_geometries[1]}

                    self.section_index += 1



    @staticmethod
    def __check_overlap(geometry1: shapely.geometry, geometry2: shapely.geometry) -> tuple[shapely.geometry, bool]:
        """
        Finds the overlap geometry between two Shapely geometries.
        Args:
            geometry1 (shapely.geometry): The first Shapely geometry.
            geometry2 (shapely.geometry): The second Shapely geometry.
        Returns:
            tuple[shapely.geometry, bool]: A tuple containing the overlap geometry
            and a boolean indicating whether there is an overlap (True) or not (False).
        Note:
            The function uses the `intersection` method from Shapely to compute the overlap
            between the two geometries.
            If the geometries do not overlap or have a point of intersection, the function
            returns an empty LineString and False.
        """
        overlap_geometry = shapely.shared_paths(geometry1, geometry2)
        # overlap_size = shapely.get_num_coordinates(overlap_geometry)

        # Convert overlap geometry type
        if isinstance(overlap_geometry, shapely.GeometryCollection):
            overlap_geometry = overlap_geometry.geoms[0]
        if isinstance(overlap_geometry, shapely.MultiLineString):
            if overlap_geometry.is_empty:
                return shapely.LineString(), False
            else:
                overlap_geometry = overlap_geometry.geoms[0]

        if isinstance(overlap_geometry, shapely.LineString):
            # print("The geometries", geometry1, "and", geometry2, "overlap in", overlap_geometry, ".")
            return overlap_geometry, True

        if isinstance(overlap_geometry, shapely.Point):
            # print("The geometries", geometry1, "and", geometry2, "are connected in", overlap_geometry, ".")
            return shapely.LineString(), False
        else:
            print('Something went wrong with determining the overlap geometry.')
            return shapely.LineString(), False

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
                if section_info['start_km'] <= km < section_info['end_km']:
                    # print("Properties at", km, "km:", section_info['properties'])
                    sections.append(section_info['properties'])
        # if len(sections) > 1:
            # print("^ This slice has two roadlines.")
        return sections

        # assert sum([]) == 1, 'Alert: more than one kantstroken property active'
