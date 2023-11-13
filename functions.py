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

    def load_data_frames(self):
        for file_path in self.file_paths:
            df_type = self.extract_df_type(file_path)
            self.data[df_type] = self.load_data_frame(file_path)

    @staticmethod
    def load_data_frame(file_path):
        return LoadDataFrame(file_path)

    @staticmethod
    def extract_df_type(file_path):
        # Folder name is extracted as the type name.
        parts = file_path.split("/")
        df_type = parts[-2]
        return df_type


def LoadDataFrame(filepath: str) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)

    # Remove unused columns
    data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

    extent = GetExtent("Vught")
    return SelectDataInExtent(data, extent)


def SelectDataInExtent(data: gpd.GeoDataFrame, extent: shapely.box) -> gpd.GeoDataFrame:
    # All data that intersects extent is considered 'in the extent'.
    data['inextent'] = data['geometry'].apply(lambda geom: intersects(geom, extent))
    return data[data['inextent']]


def GetExtent(place: str) -> shapely.box:
    definedplaces = {
        "Vught": {"north": 409832, "east": 152987, "south": 405851, "west": 148277},
        "A2VK": {"north": 348725, "east": 192000, "south": 331159, "west": 182000},
        # TODO: Add more places and coordinates.
    }

    if place in definedplaces:
        coords = definedplaces[place]
        return box(xmin=coords["west"], ymin=coords["south"], xmax=coords["east"], ymax=coords["north"])
    else:
        raise ValueError(f"Invalid place: {place}")
