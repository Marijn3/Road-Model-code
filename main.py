
import geopandas as gpd
import shapely

filepath = "data/Rijstroken/rijstroken.dbf"

data = gpd.read_file(filepath)


def ExtractLineStringCoordinates(ls: shapely.LineString) -> list[list[float, float]]:
    return list(ls.coords)


def CheckLineInExtent(lg: list[list[float, float]], extent) -> bool:
    for (x, y) in lg:
        if CheckPointInExtent(x, y, extent):
            return True
    return False


def CheckPointInExtent(x, y, extent):
    xmin, ymin, xmax, ymax = extent
    return xmin <= x <= xmax and ymin <= y <= ymax

# print(data.columns)
data_A2 = data[data['WEGNUMMER'] == '002']
# print(data_A2.head())

linestring = data_A2['geometry'][3]
linegeometry = ExtractLineStringCoordinates(linestring)
print(linegeometry)

# Determine the extent of the frame
north = 409832.1696
east = 152987.0262
south = 405851.2010
west = 148277.3982
extent = (west, south, east, north)

inExtent = CheckLineInExtent(linegeometry, extent)

print(inExtent)



