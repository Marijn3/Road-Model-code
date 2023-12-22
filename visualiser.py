from functions import *
import svgwrite

dfl = DataFrameLoader()
dfl.load_data_frames("Vught")

road = RoadModel()
road.import_dataframes(dfl)

LANE_WIDTH = 5

top_left_x, top_left_y = get_coordinates(dfl.extent)[1]
bottom_right_x, bottom_right_y = get_coordinates(dfl.extent)[3]
viewbox_width = 3*abs(top_left_x - bottom_right_x)
viewbox_height = 3*abs(top_left_y - bottom_right_y)


def svg_add_section(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    if isinstance(prop['nLanes'], int):
        road_width = LANE_WIDTH*prop['nLanes']
        roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='grey', fill="none", stroke_width=road_width)
    else:
        road_width = LANE_WIDTH * 2
        roadline = svgwrite.shapes.Polyline(points=geom.coords, stroke='red', fill="none", stroke_width=road_width)
    svg_dwg.add(roadline)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(top_left_x-viewbox_width, top_left_y-viewbox_height), size=(viewbox_width, viewbox_height), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section['geometry'], section['properties'], dwg)

# viewBox
dwg.viewbox(minx=top_left_x-viewbox_width, miny=top_left_y-viewbox_height, width=viewbox_width, height=viewbox_height)

# Save SVG file
dwg.save(pretty=True, indent=2)
