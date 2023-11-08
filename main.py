
import geopandas as gpd
from functions import *

filepath = "data/Rijstroken/rijstroken.dbf"

data = gpd.read_file(filepath)

print(data.columns)
data_A2 = data[data['WEGNUMMER'] == '002']
data_A2.drop(columns=['FK_VELD4', 'IBN'], inplace=True)
print(data_A2.head())

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



