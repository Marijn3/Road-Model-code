from functions import *

# Load all files and store the GeoDataFrames in the class
df = DataFrameLoader()
df.load_data_frames("Vught")
# df.edit_data()

# Temporary: Proof that AU and KP are always paired.
dfAU = df.data['Rijstrooksignaleringen'][df.data['Rijstrooksignaleringen']['CODE'] == 'AU']
dfKP = df.data['Rijstrooksignaleringen'][df.data['Rijstrooksignaleringen']['CODE'] == 'KP']

dfAU_lim = dfAU.sort_values(by=['geometry']).reset_index().drop(columns=['index', 'CODE', 'OMSCHR'])
dfKP_lim = dfKP.sort_values(by=['geometry']).reset_index().drop(columns=['index', 'CODE', 'OMSCHR'])

print(dfAU_lim)
print(dfKP_lim)

print(all(dfAU_lim == dfKP_lim))
