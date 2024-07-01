import matplotlib.pyplot as plt
from shapely import wkt

# Define the WKT strings
new_geom = "LINESTRING (153380.05575 412558.11998, 153387.4879 412563.3123, 153418.3934 412583.7311, 153426.6459 412589.3829, 153434.6524 412595.3778, 153438.5342 412598.5446, 153442.234 412601.8223, 153447.9919 412607.51, 153451.2234 412611.3326, 153454.2093 412615.3438, 153456.8802 412619.597, 153459.1571 412623.9754, 153460.6892 412627.789, 153462.121 412632.5922, 153463.0708 412637.5033, 153463.5643 412642.4394, 153463.2169 412650.8062, 153462.2563 412655.7138, 153460.8068 412660.5493, 153457.3594 412668.1978, 153454.7489 412672.4706, 153451.6895 412676.4263, 153448.7154 412679.6061, 153444.9671 412682.916, 153441.0106 412685.8476, 153434.7569 412689.3244, 153430.1201 412691.1984, 153425.3904 412692.6443, 153418.6994 412693.8048, 153413.7057 412694.0796, 153408.7676 412693.8906, 153403.358 412693.033, 153398.5034 412691.833, 153393.7941 412690.2117, 153388.8488 412688.0479, 153384.4481 412685.6703, 153380.1491 412683.1163, 153374.4388 412679.2671, 153362.6164 412670.035, 153341.0485 412652.0753, 153318.2379 412632.529, 153298.6946 412623.7637)"
other_geom = "LINESTRING (153456.78099 412619.43901, 153454.2093 412615.3438, 153451.2234 412611.3326, 153447.9919 412607.51, 153442.234 412601.8223, 153438.5342 412598.5446, 153434.6524 412595.3778, 153426.6459 412589.3829, 153418.3934 412583.7311, 153387.4879 412563.3123, 153380.05575 412558.11998)"
overlap = "LINESTRING (153380.05575 412558.11998, 153384.89173 412561.49854, 153387.4879 412563.3123, 153418.3934 412583.7311, 153421.21929 412585.66643, 153426.6459 412589.3829, 153434.6524 412595.3778, 153438.5342 412598.5446, 153442.234 412601.8223, 153447.9919 412607.51, 153451.2234 412611.3326, 153454.2093 412615.3438, 153456.78099 412619.43901)"

# Parse the WKT strings into LineString objects
linestring1 = wkt.loads(new_geom)
linestring2 = wkt.loads(other_geom)
linestring3 = wkt.loads(overlap)

# Plot the geometries
fig, ax = plt.subplots()
for index, line in enumerate([linestring1, linestring2, linestring3]):
    x, y = line.xy
    ax.plot(x, y, linewidth=6-2*index)

# Customize the plot
ax.set_title('Visualization of geometries')
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.legend(["New geometry", "Other geometry", "Overlap"])
ax.grid(True)

# Show the plot
plt.show()
