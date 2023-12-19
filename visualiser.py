from functions import *
import svgwrite

LANE_WIDTH = 5


def shapely_to_svg(geom, prop, svg_elem):
    if isinstance(prop['nLanes'], int):
        road_width = LANE_WIDTH*prop['nLanes']
        roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='grey', fill="none", stroke_width=road_width)
    else:
        road_width = LANE_WIDTH * 2
        roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='red', fill="none", stroke_width=road_width)
    svg_elem.add(roadline)


# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_data_frames("Vught")

road = RoadModel()
road.import_dataframes(dfl)

# Create SVG drawing
svg_drawing = svgwrite.Drawing(filename="geometries.svg")

sections = road.get_sections()
for section in sections:
    shapely_to_svg(section['geometry'], section['properties'], svg_drawing)

corner1_x, corner1_y = get_coordinates(dfl.extent)[0]
corner2_x, corner2_y = get_coordinates(dfl.extent)[2]

# Adjust the viewBox to relocate the visible portion of the SVG
viewbox_x = (corner1_x + corner2_x)/2
viewbox_y = (corner1_y + corner2_y)/2
viewbox_width = abs(corner2_x - corner1_x)
viewbox_height = abs(corner2_y - corner1_y)
svg_drawing.viewbox(minx=viewbox_x, miny=viewbox_y, width=viewbox_width, height=viewbox_height)

# Save SVG file
svg_drawing.save()
