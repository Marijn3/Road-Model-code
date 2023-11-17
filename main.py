from functions import *

# Load all files and store the GeoDataFrames in the class
df = DataFrameLoader()
df.load_data_frames("Vught")
# df.edit_data()

road = RoadModel()
road.load_from_dataframe(df.data['Rijstroken'])

# Inspect...
print(road.get_section(121.5))
