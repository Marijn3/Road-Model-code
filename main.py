
import geopandas as gpd
import shapely

filepath = "data/Rijstroken/rijstroken.dbf"

data = gpd.read_file(filepath)


def ExtractLineStringCoordinates(linestring: shapely.LineString) -> list[list[int, int]]:
    return list(linestring.coords)


# print(data.columns)
data_A2 = data[data['WEGNUMMER'] == '002']
# print(data_A2.head())

ls = data_A2['geometry'][3]
linegeometry = ExtractLineStringCoordinates(ls)
print(linegeometry)
