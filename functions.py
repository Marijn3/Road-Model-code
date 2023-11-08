import shapely
from shapely import *
import geopandas as gpd


def FindDataInExtent(filepath: str, extent: shapely.box) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)

    # Determine if data intersects extent
    data['inextent'] = data['geometry'].apply(lambda geom: intersects(geom, extent))

    return data[data['inextent']]
