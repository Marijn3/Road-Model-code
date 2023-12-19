import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (151333.63 409658.6, 151293.38 409646.63, 151281.94 409642.99)"
other_section_geom = "LINESTRING (151281.94 409642.99, 151293.38 409646.63, 151333.63 409658.6, 151366.11 409667.32, 151378.59 409670.5, 151398.04 409675.18, 151417.54 409679.62, 151501.74 409697.39, 151540.92 409705.47, 151577.2 409712.72, 151596.76 409716.92, 151616.23 409721.51, 151635.62 409726.45, 151653.43 409731.3, 151679.35 409739.04, 151698.35 409745.3, 151717.18 409752.04, 151740.4 409761.12, 151758.81 409768.96, 151777.03 409777.2, 151795.02 409785.93, 151802.92 409789.96, 151820.59 409799.33, 151838.03 409809.14, 151855.46 409819.6, 151872.37 409830.29, 151888.99 409841.4, 151903.99 409852, 151920.07 409863.9, 151935.84 409876.23, 151952.44 409889.9, 151967.62 409902.93, 151982.49 409916.38, 151997.42 409930.79, 152011.49 409945.08, 152024.21 409958.59, 152037.53 409973.5, 152050.49 409988.74, 152063.09 410004.28, 152088.38 410038.63)"
overlap_geom = "LINESTRING (151333.63 409658.60000000003, 151293.38 409646.63, 151281.94 409642.99)"
remaining_geom = "LINESTRING (151333.63 409658.6, 151366.11 409667.32, 151378.59 409670.5, 151398.04 409675.18, 151417.54 409679.62, 151501.74 409697.39, 151540.92 409705.47, 151577.2 409712.72, 151596.76 409716.92, 151616.23 409721.51, 151635.62 409726.45, 151653.43 409731.3, 151679.35 409739.04, 151698.35 409745.3, 151717.18 409752.04, 151740.4 409761.12, 151758.81 409768.96, 151777.03 409777.2, 151795.02 409785.93, 151802.92 409789.96, 151820.59 409799.33, 151838.03 409809.14, 151855.46 409819.6, 151872.37 409830.29, 151888.99 409841.4, 151903.99 409852, 151920.07 409863.9, 151935.84 409876.23, 151952.44 409889.9, 151967.62 409902.93, 151982.49 409916.38, 151997.42 409930.79, 152011.49 409945.08, 152024.21 409958.59, 152037.53 409973.5, 152050.49 409988.74, 152063.09 410004.28, 152088.38 410038.63)"

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

new_section_df.plot(ax=ax, color='blue', linewidth=12, label='New Section')
other_section_df.plot(ax=ax, color='green', linewidth=8, label='Other Section')
overlap_df.plot(ax=ax, color='orange', linewidth=4, label='Overlap')
remaining_df.plot(ax=ax, color='red', linewidth=4, label='Remaining')

# Add labels and legend
ax.set_title('Visualizing Geometries')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.legend(loc='lower right')

plt.show()
