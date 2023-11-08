import geopandas as gpd
from functions import *

filepath = "data/Divergenties/divergenties.dbf"

data = gpd.read_file(filepath)

print(data['IBN'].unique())
data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)
print(data.columns)
print(data.head())

data['x'] = data['geometry'].apply(lambda point: point.x)
data['y'] = data['geometry'].apply(lambda point: point.y)

print(data.head())

# Determine the extent of the frame
north = 409832.1696
east = 152987.0262
south = 405851.2010
west = 148277.3982
extent = (west, south, east, north)

xmin, ymin, xmax, ymax = extent

data['inextent'] = (data['x'] >= xmin) & (data['x'] <= xmax) & (data['y'] >= ymin) & (data['y'] <= ymax)

dataInExtent = data[data['inextent']]

print(dataInExtent)