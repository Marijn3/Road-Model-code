import shapely
from shapely import *
import geopandas as gpd


def FindDataInExtent(filepath: str, extent: shapely.box) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)
    print(data.columns)

    # Adapt columns
    # data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)
    #data['x'] = data['geometry'].apply(lambda point: point.x)
    #data['y'] = data['geometry'].apply(lambda point: point.y)

    data['ínextent'] = data['geometry'].apply(lambda geom: intersects(geom, box))

    print(data.head())

    # Determine data in extent
    #data['inextent'] = (data['x'] >= xmin) & (data['x'] <= xmax) & (data['y'] >= ymin) & (data['y'] <= ymax)

    return data[data['inextent']]
