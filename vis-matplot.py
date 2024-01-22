import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (148550.86788 408209.866293, 148554.8127 408213.868, 148569.3231 408227.649, 148576.2242 408233.8341, 148591.4569 408246.8728, 148607.0322 408259.4299, 148616.9517 408267.064, 148633.0608 408278.9642, 148653.5807 408293.591, 148669.9833 408305.0378, 148984.8568 408522.5018, 149201.0269 408671.6924, 149276.5065 408723.7157, 149293.0599 408734.9457, 149304.5444 408742.6767, 149321.2921 408753.6419, 149338.2986 408764.1725, 149361.473 408777.1527, 149379.2539 408786.1883, 149397.3853 408794.6324, 149409.3963 408800.0201, 149426.9414 408807.1721, 149445.6631 408814.2226, 149464.646 408820.5257, 149472.9696 408823.1047, 149492.2564 408828.4815, 149511.6963 408833.183, 149523.8633 408835.7499, 149543.5971 408839.3924, 149563.3426 408842.6446, 149583.1676 408845.2853, 149603.0439 408847.5311, 149622.9671 408849.4171, 149677.9409 408853.4945, 149697.8766 408855.1752, 149717.7399 408857.5119, 149737.5378 408860.426, 149753.7751 408863.2932, 149773.2719 408867.4135, 149792.6851 408872.2283, 149800.8967 408874.4566, 149820.0231 408880.1295, 149839.0033 408886.4344, 149861.3941 408894.776, 149879.7505 408902.5185, 149897.9816 408910.7584, 149918.2561 408921.1839, 149935.9055 408930.5896, 149979.1518 408954.4667, 150010.6764 408971.5015, 150028.6309 408980.3147, 150057.6798 408993.9096, 150075.9644 409002.0407, 150094.3779 409009.9062, 150109.0206 409015.8886, 150134.96 409031.4512)"
other_section_geom = "LINESTRING (148519.19994 408175.15772, 148540.7497 408199.6022, 148554.8127 408213.868, 148562.43265 408221.104915, 148569.3231 408227.649, 148576.2242 408233.8341, 148591.4569 408246.8728, 148607.0322 408259.4299, 148616.9517 408267.064, 148633.0608 408278.9642, 148653.5807 408293.591, 148669.9833 408305.0378, 148984.8568 408522.5018)"
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
