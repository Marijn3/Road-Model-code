import geopandas as gpd
from shapely.wkt import loads
import matplotlib.pyplot as plt

# Define the geometries
new_section_geom = "LINESTRING (106917.68030000101 406413.707199998, 106900.5055 406432.683800001, 106883.13149999801 406469.376400001, 106867.169823867 406503.858103152, 107006.97740000101 406548.41050000105, 107121.464400001 406584.3651, 107216.7038 406614.65349999804, 107229.99599999901 406618.8913, 107247.82180000101 406623.9925)"
other_section_geom = "LINESTRING (106845.5337 406549.1193, 106859.360100001 406520.7293, 106867.169823867 406503.858103152, 106850.379999999 406498.5077, 106812.2249 406486.4969, 106791.2709 406480.8884, 106780.2381 406478.633299999, 106768.0814 406477.015500002, 106756.91979999801 406476.5493, 106747.70470000099 406477.0995, 106737.520599999 406478.846999999, 106729.399900001 406481.302700002, 106720.114300001 406485.34070000105, 106711.743999999 406490.29010000103, 106704.20870000099 406496.202500001, 106697.4016 406503.007300001, 106691.9049 406509.979499999, 106685.556899998 406520.320900001, 106680.314100001 406533.9661, 106677.984099999 406545.384199999, 106677.4518 406553.77959999803, 106677.884599999 406563.280699998, 106680.0482 406574.59609999903, 106683.129099999 406583.616700001, 106687.660999998 406592.8017, 106694.2861 406602.4256, 106702.700300001 406611.368900001, 106713.1928 406619.256000001, 106725.425099999 406625.4256, 106736.697799999 406628.91340000206, 106751.033399999 406630.675700001, 106763.546 406630.08989999804, 106776.097300001 406627.3303, 106788.526000001 406622.183800001, 106799.583700001 406615.2247, 106810.998 406604.951299999, 106823.5372 406589.0539, 106833.903700002 406571.67529999797, 106845.5337 406549.1193)"
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
