from functions import *

fileConvergentie = "data/Convergenties/convergenties.dbf"
fileDivergentie = "data/Divergenties/divergenties.dbf"
fileRijstrooksignaleringen = "data/Rijstrooksignaleringen/strksignaleringn.dbf"

# Determine the extent of the frame (Vught)
north = 409832.1696
east = 152987.0262
south = 405851.2010
west = 148277.3982
extent = (west, south, east, north)

dfConvergentie = FindDataInExtent(fileConvergentie, extent)
dfDivergentie = FindDataInExtent(fileDivergentie, extent)
dfRijstrooksignaleringen = FindDataInExtent(fileRijstrooksignaleringen, extent)

# Dubbele entries rstrksgn verwijderen
dfRijstrooksignaleringen = dfRijstrooksignaleringen[dfRijstrooksignaleringen['CODE'] == 'KP']

# print(dfConvergentie.head())
# print(dfDivergentie.head())
# print(dfRijstrooksignaleringen.head())
