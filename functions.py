import shapely
from shapely import *
import geopandas as gpd


def LoadDataFrame(filepath: str) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)

    # Remove unused columns
    data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

    # Determine the extent of the frame in RD-coordinates (example: Vught)
    north = 409832.1696
    east = 152987.0262
    south = 405851.2010
    west = 148277.3982
    extent = box(xmin=west, ymin=south, xmax=east, ymax=north)

    return SelectDataInExtent(data, extent)


def SelectDataInExtent(data: gpd.GeoDataFrame, extent: shapely.box) -> gpd.GeoDataFrame:
    # All data that intersects extent is considered 'in the extent'.
    data['inextent'] = data['geometry'].apply(lambda geom: intersects(geom, extent))
    return data[data['inextent']]
