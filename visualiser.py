from functions import *
import svgwrite

LANE_WIDTH = 5

dfl = DataFrameLoader()
dfl.load_dataframes("Vught")

road = RoadModel()
road.import_dataframes(dfl)

TOP_LEFT_X, TOP_LEFT_Y = get_coordinates(dfl.extent)[2]
BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y = get_coordinates(dfl.extent)[4]
VIEWBOX_WIDTH = abs(TOP_LEFT_X - BOTTOM_RIGHT_X)
VIEWBOX_HEIGHT = abs(TOP_LEFT_Y - BOTTOM_RIGHT_Y)
RATIO = VIEWBOX_HEIGHT / VIEWBOX_WIDTH


def get_road_color(prop: dict) -> str:
    # if 'nRijstroken' not in prop.keys():
    #     return 'orange'

    # if not isinstance(prop['nRijstroken'], int):
    #     return 'red'

    return 'grey'


def get_road_width(prop: dict) -> int:
    n_lanes = max([lane_number for lane_number in prop.keys() if isinstance(lane_number, int)])
    return LANE_WIDTH*n_lanes


def get_transformed_coords(geom: LineString) -> list[tuple]:
    return [(point[0], TOP_LEFT_Y - (point[1] - TOP_LEFT_Y)) for point in geom.coords]


def get_offset_coords(geom: LineString, offset: float) -> list[tuple]:
    if offset == 0:
        return [(point[0], TOP_LEFT_Y - (point[1] - TOP_LEFT_Y)) for point in geom.coords]
    else:
        geom2 = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
        return [(point[0], TOP_LEFT_Y - (point[1] - TOP_LEFT_Y)) for point in geom2.coords]


def svg_add_section(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    color = get_road_color(prop)
    width = get_road_width(prop)
    coords = get_transformed_coords(geom)
    roadline = svgwrite.shapes.Polyline(points=coords,
                                        stroke=color,
                                        fill="none",
                                        stroke_width=width)
    svg_dwg.add(roadline)

    add_separator_lines(geom, prop, svg_dwg)


def add_separator_lines(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    n_lanes = max([lane_number for lane_number in prop.keys() if isinstance(lane_number, int)])
    n_dashes = n_lanes + 1

    # Centered around 0
    offsets = [LANE_WIDTH*i - (LANE_WIDTH*n_lanes)/2 for i in range(0, n_dashes)]

    # Add 'left' solid line
    line_coords = get_offset_coords(geom, offsets.pop(0))
    dash_line = svgwrite.shapes.Polyline(points=line_coords,
                                         stroke="white",
                                         fill="none",
                                         stroke_width=0.4)
    svg_dwg.add(dash_line)

    # Add 'right' solid line
    line_coords = get_offset_coords(geom, offsets.pop(-1))
    dash_line = svgwrite.shapes.Polyline(points=line_coords,
                                         stroke="white",
                                         fill="none",
                                         stroke_width=0.4)
    svg_dwg.add(dash_line)

    for offset in offsets:
        line_coords = get_offset_coords(geom, offset)
        dash_line = svgwrite.shapes.Polyline(points=line_coords,
                                             stroke="white",
                                             fill="none",
                                             stroke_width=0.4,
                                             stroke_dasharray="8")
        svg_dwg.add(dash_line)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000 * RATIO))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section['geometry'], section['properties'], dwg)

# viewBox
dwg.viewbox(minx=TOP_LEFT_X, miny=TOP_LEFT_Y, width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisation finished successfully.")
