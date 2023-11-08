import geopandas as gpd
from functions import *

filepath = "data/Divergenties/divergenties.dbf"

data = gpd.read_file(filepath)

data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)
print(data.columns)
print(data.head())

data['geometry'] = data['geometry'].astype(str)
data[['x', 'y']] = data['geometry'].str.extract(r'POINT \((\d+\.\d+) (\d+\.\d+)\)').astype(float)

print(data.head())

# Determine the extent of the frame
north = 409832.1696
east = 152987.0262
south = 405851.2010
west = 148277.3982
extent = (west, south, east, north)

# for i in data.index:
#     ls = ExtractLineStringCoordinates(data_A2['geometry'][i])
#     print(ls)
#     data_A2.loc[i, 'inextent'] = CheckLineInExtent(ls, extent)
#
# print(data_A2.head())
# print(data_A2[data_A2['inextent'] == True].head())



