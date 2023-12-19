from functions import *
import svgwrite

LANE_WIDTH = 15


def shapely_to_svg(geom, prop, svg_elem):
    if isinstance(prop['nLanes'], int):
        road_width = LANE_WIDTH*prop['nLanes']
        roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='grey', fill="none", stroke_width=road_width)
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
    geom = section['geometry']
    prop = section['properties']
    shapely_to_svg(geom, prop, svg_drawing)

print(dfl.extent)

viewbox_x = 148300  # Adjust as needed
viewbox_y = 405800  # Adjust as needed
viewbox_width = 1000  # Adjust as needed
viewbox_height = 20000  # Adjust as needed
svg_drawing.viewbox(minx=viewbox_x, miny=viewbox_y, width=viewbox_width, height=viewbox_height)


# Save SVG file
svg_drawing.save()
