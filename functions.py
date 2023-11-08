import shapely
import geopandas as gpd


def FindDataInExtent(filepath: str, extent: tuple[4]) -> gpd.GeoDataFrame:
    data = gpd.read_file(filepath)
    print(data.columns)
    # print(data.head())
    # print(data['IBN'].unique())

    # Adapt columns
    # data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)
    data['x'] = data['geometry'].apply(lambda point: point.x)
    data['y'] = data['geometry'].apply(lambda point: point.y)

    # Determine data in extent
    xmin, ymin, xmax, ymax = extent
    data['inextent'] = (data['x'] >= xmin) & (data['x'] <= xmax) & (data['y'] >= ymin) & (data['y'] <= ymax)

    return data[data['inextent']]


def ExtractLineStringCoordinates(ls: shapely.LineString) -> list[list[float, float]]:
    return list(ls.coords)
