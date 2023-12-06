from functions import *

# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_data_frames("Vught")
# df.edit_data()

road = RoadModel()
road.import_dataframes(dfl)

# Inspect...
geom = road.get_properties_at(121.6, 'L')
print(geom)

# A way to find if two geometries have overlap.
print(shapely.get_num_coordinates(shapely.shared_paths(geom[0], geom[1])))
print(shapely.get_num_coordinates(shapely.shared_paths(geom[0], geom[2])))
print(shapely.get_num_coordinates(shapely.shared_paths(geom[0], geom[3])))

print(shapely.get_num_coordinates(shapely.shared_paths(geom[1], geom[2])))
print(shapely.get_num_coordinates(shapely.shared_paths(geom[1], geom[3])))
