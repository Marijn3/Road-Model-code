from functions import *

# Load all files and store the GeoDataFrames in the class
df = DataFrameLoader()
df.load_data_frames("Vught")

# Remove double entries
df.data['Rijstrooksignaleringen'] = df.data['Rijstrooksignaleringen'][df.data['Rijstrooksignaleringen']['CODE'] == 'KP']

print(df.data['Convergenties'])
print(df.data['Divergenties'])
print(df.data['Rijstroken'][['geometry', 'inextent']].head())
