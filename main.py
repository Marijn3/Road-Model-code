from functions import *

fileConvergentie           = "data/Convergenties/convergenties.dbf"
fileDivergentie            = "data/Divergenties/divergenties.dbf"
fileRijstrooksignaleringen = "data/Rijstrooksignaleringen/strksignaleringn.dbf"
fileMengstroken            = "data/Mengstroken/mengstroken.dbf"
fileRijstroken             = "data/Rijstroken/rijstroken.dbf"

dfConvergentie           = LoadDataFrame(fileConvergentie)
dfDivergentie            = LoadDataFrame(fileDivergentie)
dfRijstrooksignaleringen = LoadDataFrame(fileRijstrooksignaleringen)
dfMengstroken            = LoadDataFrame(fileMengstroken)
dfRijstroken             = LoadDataFrame(fileRijstroken)

# Remove double entries
dfRijstrooksignaleringen = dfRijstrooksignaleringen[dfRijstrooksignaleringen['CODE'] == 'KP']

print(dfRijstroken[['geometry', 'inextent']].head())
