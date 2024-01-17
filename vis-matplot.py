import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (151394.2343 409641.2272, 151423.5126 409647.877, 151444.3528 409652.3467, 151473.7304 409658.3204, 151574.2867 409677.4273, 151598.8001 409682.3362, 151633.7952 409690.1455, 151657.9814 409696.4723, 151687.3793 409705.1023, 151706.3753 409711.3686, 151720.5192 409716.3638, 151721.2934286 409716.6638039)"
other_section_geom = "LINESTRING (151394.2343 409641.2272, 151423.5126 409647.877, 151444.3528 409652.3467, 151473.7304 409658.3204, 151574.2867 409677.4273, 151598.8001 409682.3362, 151633.7952 409690.1455, 151657.9814 409696.4723, 151687.3793 409705.1023, 151703.6857316 409710.4813794, 151706.3753 409711.3686, 151720.5192 409716.3638, 151720.519421 409716.3638856, 151721.2934286 409716.6638039)"
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
other_section_df.plot(ax=ax, color='orange', linewidth=8, label='Other section')
# overlap_df.plot(ax=ax, color='green', linestyle="dashed", linewidth=2, label='Overlap')
# remaining_df.plot(ax=ax, color='purple', linestyle="dotted", linewidth=2, label='Remaining')

# Set limits based on the coordinates of the new section
# xmin, ymin, xmax, ymax = new_section_geometry.bounds
# ax.set_xlim(xmin, xmax)
# ax.set_ylim(ymin, ymax)

# Add labels and legend
ax.set_title('Geometry visualisation')
ax.set_xlabel('X Coordinate (m)')
ax.set_ylabel('Y Coordinate (m)')
ax.legend(loc='lower right')

plt.show()
