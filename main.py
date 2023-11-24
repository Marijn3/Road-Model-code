from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_data_frames("Vught")
# df.edit_data()

road = RoadModel()
road.import_dataframe(dfl, 'Rijstroken')

# Inspect...
print(road.get_properties_at(121.5))
