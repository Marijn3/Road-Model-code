from functions import *
import svgwrite

dfl = DataFrameLoader()
dfl.load_data_frames("Vught")

road = RoadModel()
road.import_dataframes(dfl)

LANE_WIDTH = 5

corner1_x, corner1_y = get_coordinates(dfl.extent)[0]
corner2_x, corner2_y = get_coordinates(dfl.extent)[2]
viewbox_x = (corner1_x + corner2_x)/2
viewbox_y = (corner1_y + corner2_y)/2
viewbox_width = abs(corner2_x - corner1_x)
viewbox_height = abs(corner2_y - corner1_y)


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
dwg.add(svgwrite.shapes.Rect(insert=(viewbox_x, viewbox_y), size=(viewbox_width, viewbox_height), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section['geometry'], section['properties'], dwg)

# viewBox
dwg.viewbox(minx=viewbox_x, miny=viewbox_y, width=viewbox_width, height=viewbox_height)

# Save SVG file
dwg.save(pretty=True, indent=2)
