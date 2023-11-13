import shapely
from shapely import *
import geopandas as gpd
import csv


class DataFrameLoader:
    def __init__(self):
        # List all files to be loaded.
        self.file_paths = [
            "data/Convergenties/convergenties.dbf",
            "data/Divergenties/divergenties.dbf",
            "data/Rijstrooksignaleringen/strksignaleringn.dbf",
            "data/Rijbanen/rijbanen.dbf",
            "data/Rijstroken/rijstroken.dbf",
            "data/Kantstroken/kantstroken.dbf",
            "data/Mengstroken/mengstroken.dbf",
            "data/Maximum snelheid/max_snelheden.dbf",
            "data/Signaleringen/signaleringen.dbf",
            "data/Wegcategorie naar beleving/wegcat_beleving.dbf"
        ]
        self.data = {}
        self.extent = None

    # Use this function to load data for a specific location.
    def load_data_frames(self, location: str):
        self.get_extent(location)
        for file_path in self.file_paths:
            df_layer_name = self.get_layer_name(file_path)
            self.data[df_layer_name] = self.load_data_frame(file_path)

    def load_data_frame(self, file_path: str) -> gpd.GeoDataFrame:
        data = gpd.read_file(file_path)
        self.drop_columns(data)
        return self.select_data_in_extent(data)

    def get_extent(self, location: str) -> shapely.box:
        coords = self.load_extent_from_csv(location)

        if coords:
            self.extent = box(xmin=coords["west"], ymin=coords["south"], xmax=coords["east"], ymax=coords["north"])
        else:
            raise ValueError(f"Invalid place: {location}")

    @staticmethod
    def get_layer_name(file_path) -> str:
        # Folder name is extracted as the name.
        parts = file_path.split("/")
        folder_name = parts[-2]
        return folder_name

    @staticmethod
    def drop_columns(data: gpd.GeoDataFrame):
        # These columns are unused
        data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

    def select_data_in_extent(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        # All data that intersects extent is considered 'in the extent'.
        data['inextent'] = data['geometry'].apply(lambda geom: geom.intersects(self.extent))
        return data[data['inextent']]

    @staticmethod
    def load_extent_from_csv(location: str) -> dict:
        with open('data/locations.csv', 'r') as file:
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
