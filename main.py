from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_dataframes("Vught")

# Construct a road model using the GeoDataFrames
road = RoadModel()
road.import_dataframes(dfl)

# Inspect...
road.get_properties_at(121.6, 'L')  # Two sections
road.get_properties_at(121.8, 'L')  # One section
road.get_properties_at(110.9, 'L')  # No sections
road.get_properties_at(121.6, 'R')  # Other side of road
