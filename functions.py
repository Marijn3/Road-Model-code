import shapely
from shapely import *
import geopandas as gpd


def LoadDataFrame(filepath: str) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)

    # Remove unused columns
    data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

    extent = getExtent("Vught")
    return SelectDataInExtent(data, extent)


def getExtent(place: str) -> shapely.box:
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


def SelectDataInExtent(data: gpd.GeoDataFrame, extent: shapely.box) -> gpd.GeoDataFrame:
    # All data that intersects extent is considered 'in the extent'.
    data['inextent'] = data['geometry'].apply(lambda geom: intersects(geom, extent))
    return data[data['inextent']]
