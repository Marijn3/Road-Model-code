from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_data_frames("Vught")

road = RoadModel()
road.import_dataframes(dfl)

# Inspect...
road.get_properties_at(121.6, 'L')