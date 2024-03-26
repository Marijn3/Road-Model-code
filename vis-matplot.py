import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (118186.6877 483391.0439, 118301.795 483400.0936, 118408.233 483408.7424, 118574.9253 483421.9956, 118615.0733 483421.5513, 118932.1954 483446.5271, 118986.9157 483450.536, 119026.5443 483457.4355, 119211.765 483472.0851, 119285.8538 483477.6361, 119329.136 483480.6121, 119490.9974 483491.4972, 119522.70553 483493.52657)"
other_section_geom = "LINESTRING (118986.9157 483450.536, 119013.2801 483445.1117, 119062.296 483447.4747, 119068.7964 483447.5246, 119073.7955 483447.3396, 119078.7772 483446.8829, 119083.7498 483446.1556)"
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
