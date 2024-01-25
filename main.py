from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_dataframes("A2Vink")

# Construct a road model using the GeoDataFrames
roadmodel = RoadModel()
roadmodel.import_dataframes(dfl)

# Inspect for DEMO (Vught)
roadmodel.get_properties_at(121.6, 'L')  # Two sections
roadmodel.get_properties_at(121.8, 'L')  # One section
roadmodel.get_properties_at(110.9, 'L')  # No sections
roadmodel.get_properties_at(121.4, 'R')  # Other side of road, narrowing lanes.

MSIs = MSINetwork(roadmodel)
