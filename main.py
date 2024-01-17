from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_dataframes("Vught")

road = RoadModel()
road.import_dataframes(dfl)

# Inspect...
road.get_properties_at(121.6, 'L')
road.get_properties_at(121.8, 'L')
road.get_properties_at(110.9, 'R')
road.get_properties_at(121.6, 'R')
