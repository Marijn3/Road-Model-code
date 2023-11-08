from functions import *
from shapely import box

fileConvergentie = "data/Convergenties/convergenties.dbf"
fileDivergentie = "data/Divergenties/divergenties.dbf"
fileRijstrooksignaleringen = "data/Rijstrooksignaleringen/strksignaleringn.dbf"
fileMengstroken = "data/Mengstroken/mengstroken.dbf"
fileRijstroken = "data/Rijstroken/rijstroken.dbf"

# Determine the extent of the frame (Vught)
north = 409832.1696
east = 152987.0262
south = 405851.2010
west = 148277.3982
extent = box(xmin=west, ymin=south, xmax=east, ymax =north)

dfConvergentie = FindDataInExtent(fileConvergentie, extent)
dfDivergentie = FindDataInExtent(fileDivergentie, extent)
dfRijstrooksignaleringen = FindDataInExtent(fileRijstrooksignaleringen, extent)
dfMengstroken = FindDataInExtent(fileMengstroken, extent)
dfRijstroken = FindDataInExtent(fileRijstroken, extent)

# Dubbele entries rstrksgn verwijderen
dfRijstrooksignaleringen = dfRijstrooksignaleringen[dfRijstrooksignaleringen['CODE'] == 'KP']

# Adapt columns
# data.drop(columns=['FK_VELD4', 'IBN'], inplace=True)

print(dfRijstroken[['geometry', 'inextent']].head())