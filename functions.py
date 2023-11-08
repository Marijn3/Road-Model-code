import shapely
from shapely import *
import geopandas as gpd


def FindDataInExtent(filepath: str, extent: shapely.box) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)
    # print(data.columns)

    # Adapt columns
    data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

    # Determine if data intersects extent
    data['inextent'] = data['geometry'].apply(lambda geom: intersects(geom, extent))

    print(data[['geometry', 'inextent']].head())

    return data[data['inextent']]
