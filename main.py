
import geopandas as gpd

filepath = "data/Rijstroken/rijstroken.dbf"

# Read file using gpd.read_file()
data = gpd.read_file(filepath)

print(data.head(2))
