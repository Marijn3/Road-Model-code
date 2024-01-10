import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (149113 408163, 149112 408173, 149112 408180, 149110 408258)"
other_section_geom = "LINESTRING (149110 408238, 149110 408258, 149109 408287, 149107 408308, 149103 408325, 149096 408343, 149086 408359, 149073 408376, 149067 408383)"
overlap_geom = "LINESTRING (149113 408163, 149112 408173, 149112 408180, 149110 408258)"
remaining_geom = "LINESTRING (149109 408287, 149107 408308, 149103 408325, 149096 408343, 149086 408359, 149073 408376, 149067 408383)"
# overlap_geom = "LINESTRING (149109 408287, 149107 408302)"
# remaining_geom = "LINESTRING (149110 408238, 149110 408258)"

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
overlap_df.plot(ax=ax, color='red', linewidth=4, label='Overlap')
remaining_df.plot(ax=ax, color='orange', linewidth=2, label='Overlap 2')

# Add labels and legend
ax.set_title('Visualizing Geometries')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.legend(loc='lower right')

plt.show()
