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

        side_b = row['IZI_SIDE']
        begin_b = row['BEGINKM']
        end_b = row['EINDKM']
        prop_b = row[columns_of_interest].to_dict()
        geom_b = row['geometry']

        # Method to handle propagating properties with intersecting sections.
        # Determine overlapping section
        overlap_present = False
        for section_index, section in self.sections.items():
            overlap, overlap_size = self.__check_overlap(geom_b, section['geometry'])
            overlap_present = overlap_size != 0  # If overlap geometry size is not 0, there is overlap
            if overlap_present:
                overlap_section = section
                overlap_index = section_index
                print(section, section_index)
                # Assumption that sections only intersect with ONE other section
                # TODO: Remove assumption
                break

        # Determine overlap case
        if overlap_present:
            begin_a = overlap_section['start_km']
            end_a = overlap_section['end_km']
            begin_b = begin_b
            end_b = end_b
            if begin_a == begin_b or end_a == end_b:
                if begin_a == begin_b and end_a == end_b:
                    # Fully equal case. 1 resulting section. 1 possible combination.
                    print('Found equal geometries with equal start and end. Combining the properties...')
                    # print(self.sections[overlap_index]['properties'])
                    self.sections[overlap_index]['properties'].update(prop_b)  # add new property
                    # print(self.sections[overlap_index]['properties'])
                    # Adjust geometry if necessary
                else:
                    # 1/2 equal case. 2 resulting sections. 4 possible combinations.
                    print('Found equal geometries with equal start OR end. Determining sections...')

                    geom_a_and_b = overlap_section['geometry']
                    prop_a = overlap_section['properties'].copy()
                    geom_a = geom_a_and_b.symmetric_difference(geom_b)

                    # [Update overlapping section]
                    # Update start or end point (using midpoint)
                    if begin_a == begin_b:
                        midpoint = min(end_a, end_b)
                        self.sections[overlap_index]['end_km'] = midpoint
                    if end_a == end_b:
                        midpoint = max(begin_a, begin_b)
                        self.sections[overlap_index]['start_km'] = midpoint
                    # Reduce geometry
                    self.sections[overlap_index]['geometry'] = geom_b
                    # Update properties
                    self.sections[overlap_index]['properties'].update(prop_b)

                    # [Add remaining section]
                    if begin_a == begin_b:
                        begin = midpoint
                        end = max(end_a, end_b)
                    if end_a == end_b:
                        begin = max(begin_a, begin_b)
                        end = midpoint

                    self.sections[self.section_index] = {'side': side_b,
                                                         'start_km': begin,
                                                         'end_km': end,
                                                         'properties': prop_a,
                                                         'geometry': geom_a}

                    # Verify results (TEMP)
                    print(self.sections[overlap_index])
                    print(self.sections[self.section_index])

                    self.section_index += 1

            else:
                print('0/2')
                # 0/2 equal case. 3 resulting sections. 4 possible combinations
        else:
            # Add section regularly
            self.sections[self.section_index] = {'side': side_b,
                                                 'start_km': begin_b,
                                                 'end_km': end_b,
                                                 'properties': prop_b,
                                                 'geometry': geom_b}
            self.section_index += 1


    @staticmethod
    def __check_overlap(geometry1: shapely.geometry, geometry2: shapely.geometry) -> tuple[shapely.geometry, int]:
        """
        """
        overlap = shapely.shared_paths(geometry1, geometry2)
        overlap_size = shapely.get_num_coordinates(overlap)
        # print("There is", overlap_size, "overlap with existing geometries.")
        return overlap, overlap_size

    def get_properties_at(self, km: float, side: str) -> list:
        """
        Find the properties of a road section at a specific km.
        Args:
            km (float): Kilometer point to retrieve the road section for.
            side (str): Side of the road to retrieve the road section for.
        Returns:
            list: Attributes of the road section at the specified kilometer point.
        """
        geom = []
        for section_index, section_info in self.sections.items():
            if section_info['side'] == side:
                if section_info['start_km'] <= km <= section_info['end_km']:
                    print(section_info['properties'])
                    geom.append(section_info['geometry'])
        return geom

        # assert sum([]) == 1, 'Alert: more than one kantstroken property active'
