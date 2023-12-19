from functions import *
import svgwrite

LANE_WIDTH = 15

# Define the geometries
geom1 = LineString([(200, 300), (400, 100), (900, 500)])
geom2 = LineString([(400, 350), (600, 500), (200, 600)])
prop1 = {'nLanes': 3}
prop2 = {'nLanes': 2}

# Create SVG drawing
svg_drawing = svgwrite.Drawing(filename="geometries.svg")


def shapely_to_svg(geom, prop, svg_elem):
    road_width = LANE_WIDTH*prop['nLanes']
    roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='grey', fill="none", stroke_width=road_width)
    svg_elem.add(roadline)


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
