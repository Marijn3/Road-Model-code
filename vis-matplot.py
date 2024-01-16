import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (149107.3768309 408301.8986982, 149108.68948 408287.45953, 149109.95949 408257.61447, 149112 408180, 149112.1989 408173.36997, 149112.8095704 408163.0330741)"
other_section_geom = "LINESTRING (149067.10634 408383.3734495, 149072.68099999998 408375.59599999996, 149086.30568999998 408359.05591999996, 149095.98945999998 408342.70463999995, 149102.65696999998 408325.40086, 149106.78448 408308.41456999996, 149108.68948 408287.45953, 149109.95948999998 408257.61447, 149110.4753704 408237.9920308)"
overlap_geom = "LINESTRING (149110 408258, 149110 408238)"
remaining_geom = "LINESTRING (149067.10634 408383.3734495, 149072.681 408375.596, 149086.30569 408359.05592, 149095.98946 408342.70464, 149102.65697 408325.40086, 149106.78448 408308.41457, 149107.3768309 408301.8986982)"

# Convert WKT to Shapely geometries
new_section_geometry = loads(new_section_geom)
other_section_geometry = loads(other_section_geom)
overlap_geometry = loads(overlap_geom)
remaining_geometry = loads(remaining_geom)

# Create GeoDataFrames
new_section_df = gpd.GeoDataFrame(geometry=[new_section_geometry], columns=['geometry'])
other_section_df = gpd.GeoDataFrame(geometry=[other_section_geometry], columns=['geometry'])
overlap_df = gpd.GeoDataFrame(geometry=[overlap_geometry], columns=['geometry'])
remaining_df = gpd.GeoDataFrame(geometry=[remaining_geometry], columns=['geometry'])

# Plot the geometries
fig, ax = plt.subplots(figsize=(10, 8))

new_section_df.plot(ax=ax, color='blue', linewidth=12, label='New section')
other_section_df.plot(ax=ax, color='green', linewidth=8, label='Other section')
overlap_df.plot(ax=ax, color='orange', linewidth=2,)
remaining_df.plot(ax=ax, color='orange', linewidth=2, label='Remaining')

# Set limits based on the coordinates of the "New section"
# xmin, ymin, xmax, ymax = new_section_geometry.bounds
# ax.set_xlim(xmin, xmax)
# ax.set_ylim(ymin, ymax)

# Add labels and legend
ax.set_title('Geometry visualisation.')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.legend(loc='lower right')

plt.show()
