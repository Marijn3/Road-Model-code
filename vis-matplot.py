import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (150894.00000000003 409646.00000000006, 150909.76720000003 409648.71960000007, 150914.64365 409649.82411000005)"
other_section_geom = "LINESTRING (150894 409646, 150909.7672 409648.7196, 150917.5792 409650.489, 150921.5882 409650.7848, 150960.0034 409652.4399, 150977.5581 409652.897, 150987.5904 409652.2659, 150998.3525 409651.2898, 151008.1991 409649.6762, 151018.1662 409647.1954, 151022.8668 409645.4544, 151027.6109 409643.2782, 151035.1634 409638.3121, 151039.0653 409635.1575, 151043.87 409630.0219, 151046.8577 409625.9177, 151049.4346 409621.6324, 151051.5947 409616.6905, 151053.256 409611.932, 151054.1949 409607.0187, 151054.7248 409602.6054, 151054.7679 409597.5823, 151053.8617 409589.0055, 151052.4426 409584.1719, 151050.7932 409579.4516, 151048.6082 409575.2862, 151046.073 409570.9392, 151043.0075 409566.989, 151039.2796 409562.7614, 151035.58 409559.3208, 151031.7673 409556.0819, 151023.7117 409550.1456, 151019.4026 409547.3113, 151010.9696 409541.9309, 150930.26 409491.8161, 150895.4492 409461.8162)"
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
