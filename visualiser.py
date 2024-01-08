from functions import *
import svgwrite

LANE_WIDTH = 5

dfl = DataFrameLoader()
dfl.load_dataframes("Vught")

road = RoadModel()
road.import_dataframes(dfl)

top_left_x, top_left_y = get_coordinates(dfl.extent)[2]
bottom_right_x, bottom_right_y = get_coordinates(dfl.extent)[4]
viewbox_width = abs(top_left_x - bottom_right_x)
viewbox_height = abs(top_left_y - bottom_right_y)
ratio = viewbox_height/viewbox_width


def get_road_color(prop: dict) -> str:
    # if 'nRijstroken' not in prop.keys():
    #     return 'orange'
    if 'nRijstroken' in prop.keys():
        if not isinstance(prop['nRijstroken'], int):
            return 'red'

    return 'grey'


def get_road_width(prop: dict) -> int:
    if 'nRijstroken' in prop.keys():
        if isinstance(prop['nRijstroken'], int):
            return LANE_WIDTH*prop['nRijstroken']

    return LANE_WIDTH


def get_transformed_coords(coords: list[tuple]) -> list[tuple]:
    return [(point[0], top_left_y - (point[1] - top_left_y)) for point in coords]


def svg_add_section(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    color = get_road_color(prop)
    width = get_road_width(prop)
    coords = get_transformed_coords(geom.coords)
    roadline = svgwrite.shapes.Polyline(points=coords, stroke=color, fill="none", stroke_width=width)
    svg_dwg.add(roadline)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000*ratio))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(top_left_x, top_left_y), size=(viewbox_width, viewbox_height), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section['geometry'], section['properties'], dwg)

# viewBox
dwg.viewbox(minx=top_left_x, miny=top_left_y, width=viewbox_width, height=viewbox_height)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisation finished successfully.")
