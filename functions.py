import shapely
from shapely import *
import geopandas as gpd


class DataFrameLoader:
    def __init__(self):
        self.file_paths = [
            "data/Convergenties/convergenties.dbf",
            "data/Divergenties/divergenties.dbf",
            "data/Rijstrooksignaleringen/strksignaleringn.dbf",
            "data/Mengstroken/mengstroken.dbf",
            "data/Rijstroken/rijstroken.dbf"
        ]
        self.data = {}
        self.extent = None

    # Use this function to load data for a specific location.
    def load_data_frames(self, place: str):
        self.get_extent(place)
        for file_path in self.file_paths:
            df_layer_name = self.get_layer_name(file_path)
            self.data[df_layer_name] = self.load_data_frame(file_path)

    def load_data_frame(self, file_path: str) -> gpd.GeoDataFrame:
        data = gpd.read_file(file_path)
        self.drop_columns(data)
        return self.select_data_in_extent(data)

    def get_extent(self, place: str) -> shapely.box:
        definedplaces = {
            "Vught": {"north": 409832, "east": 152987, "south": 405851, "west": 148277},
            "A2VK": {"north": 348725, "east": 192000, "south": 331159, "west": 182000},
            # TODO: Add more places and coordinates.
        }

        if place in definedplaces:
            coords = definedplaces[place]
            self.extent = box(xmin=coords["west"], ymin=coords["south"], xmax=coords["east"], ymax=coords["north"])
        else:
            raise ValueError(f"Invalid place: {place}")

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
