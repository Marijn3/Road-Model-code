from functions import *

# Load all files and store the GeoDataFrames in the class
df = DataFrameLoader()
df.load_data_frames()

# Now you can access the DataFrames using logical names
print(df.data['Convergenties'])
print(df.data['Divergenties'])

# Remove double entries
df.data['Rijstrooksignaleringen'] = df.data['Rijstrooksignaleringen'][df.data['Rijstrooksignaleringen']['CODE'] == 'KP']

print(df.data['Rijstroken'][['geometry', 'inextent']].head())
