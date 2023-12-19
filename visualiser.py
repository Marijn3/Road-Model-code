from functions import *
import svgwrite

# Define the geometries
geom1 = LineString([(200, 300), (400, 100), (900, 500)])
geom2 = LineString([(400, 350), (600, 500), (200, 600)])
prop1 = {'nLanes': 3}
prop2 = {'nLanes': 2}

# Create SVG drawing
svg_drawing = svgwrite.Drawing(filename="geometries.svg")


# Function to convert Shapely geometry to SVG
def shapely_to_svg(geom, prop, svg_elem):
    if geom.geom_type == 'LineString':
        svg_elem.add(svgwrite.shapes.Polyline(points=geom.coords, stroke='grey', fill="none", stroke_width=12*prop['nLanes']))
    elif geom.geom_type == 'MultiLineString':
        for line in geom:
            svg_elem.add(svgwrite.shapes.Polyline(points=line.coords, stroke='grey', fill="none", stroke_width=12*prop['nLanes']))

# Convert Shapely geometries to SVG
shapely_to_svg(geom1, prop1, svg_drawing)
shapely_to_svg(geom2, prop2, svg_drawing)

# Save SVG file
svg_drawing.save()



# # Load all files and store the GeoDataFrames in the class
# dfl = DataFrameLoader()
# dfl.load_data_frames("Vught")
#
# road = RoadModel()
# road.import_dataframes(dfl)
#
# # Inspect...
# road.get_properties_at(121.6, 'L')