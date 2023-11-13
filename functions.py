import geopandas as gpd
import pandas as pd
import shapely.geometry
from shapely.geometry import box
import csv


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
        "data/Convergenties/convergenties.dbf",
        "data/Divergenties/divergenties.dbf",
        "data/Rijstrooksignaleringen/strksignaleringn.dbf",
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        "data/Mengstroken/mengstroken.dbf",
        "data/Maximum snelheid/max_snelheden.dbf",
    ]

    def __init__(self):
        self.data = {}
        self.extent = None

    # Call this to load data for a specific location.
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
            self.__drop_columns(self.data[df_layer_name])
            self.__edit_columns(self.data[df_layer_name])
            self.data[df_layer_name].info()

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

    @staticmethod
    def __drop_columns(data: gpd.GeoDataFrame):
        """
        Drop unused columns from the GeoDataFrame.
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        """
        # These columns are not necessary in this project.
        data.drop(columns=['FK_VELD4', 'IBN', 'inextent'], inplace=True)

    @staticmethod
    def __edit_columns(data: gpd.GeoDataFrame):
        """
        Edit columns variable types of the GeoDataFrame.
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        """
        # These column variable types should be changed.
        data['WEGNUMMER'] = pd.to_numeric(data['WEGNUMMER'], errors='coerce').astype('Int64')

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

    def edit_data(self):
        """ TODO: Docstring """

        # Select only the KP (kruis-pijl) signalling in Rijstrooksignaleringen
        self.data['Rijstrooksignaleringen'] = (
            self.data)['Rijstrooksignaleringen'][self.data['Rijstrooksignaleringen']['CODE'] == 'KP']

