from functions import *

# Load all files and store the GeoDataFrames in the class
df = DataFrameLoader()
df.load_data_frames("Vught")
df.edit_data()
