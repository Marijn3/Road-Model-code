from functions import *
import svgwrite

LANE_WIDTH = 3.5

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
    # if 'Puntstuk' in prop.values():
    #     return 'dimgrey'

    # if not isinstance(prop['nRijstroken'], int):
    #     return 'red'

    return 'grey'


def get_n_lanes(prop: dict) -> int:
    n_lanes = max([lane_number for (lane_number, lane_type) in prop.items() if (isinstance(lane_number, int) and lane_type not in ['Puntstuk'])])
    print(n_lanes)
    return n_lanes


def get_road_width(prop: dict) -> float:
    return LANE_WIDTH*get_n_lanes(prop)


def get_transformed_coords(geom: LineString | Point) -> list[tuple]:
    return [(coord[0], TOP_LEFT_Y - (coord[1] - TOP_LEFT_Y)) for coord in geom.coords]


def get_offset_coords(geom: LineString, offset: float) -> list[tuple]:
    if offset == 0:
        return get_transformed_coords(geom)
    else:
        offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
        return get_transformed_coords(offset_geom)


def svg_add_section(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    color = get_road_color(prop)
    width = get_road_width(prop)
    coords = get_transformed_coords(geom)

    asphalt = svgwrite.shapes.Polyline(points=coords, stroke=color, fill="none", stroke_width=width)
    svg_dwg.add(asphalt)

    add_separator_lines(geom, prop, svg_dwg)


def add_separator_lines(geom: LineString, prop: dict, svg_dwg: svgwrite.Drawing):
    n_lanes = get_n_lanes(prop)
    print(prop)

    # Offset centered around 0. Positive offset distance is on the left side of the line.
    offsets = [(LANE_WIDTH*n_lanes)/2 - LANE_WIDTH*i for i in range(n_lanes+1)]

    # Add first line (left).
    line_coords = get_offset_coords(geom, offsets.pop(0))
    add_markerline(line_coords, svg_dwg)

    for lane_nr in range(1, n_lanes+1):
        line_coords = get_offset_coords(geom, offsets.pop(0))

        # To handle missing road numbers (due to taper) temporarily.
        if lane_nr not in prop.keys():
            continue

        # Stop when this is the final roadline (right).
        if lane_nr+1 not in prop.keys():
            add_markerline(line_coords, svg_dwg)
            break

        # An emergency lane is always the final, rightmost lane.
        if prop[lane_nr+1] == 'Vluchtstrook':
            add_markerline(line_coords, svg_dwg)
            break

        # A puntstuk is always the final, rightmost lane.
        if prop[lane_nr + 1] == 'Puntstuk':
            add_markerline(line_coords, svg_dwg, "point")
            break

        # All other lanes are separated by dashed lines.
        if prop[lane_nr] == prop[lane_nr+1]:
            add_markerline(line_coords, svg_dwg, "dashed")
        # If the lane types are not the same, block markings are used.
        else:
            add_markerline(line_coords, svg_dwg, "block")


def add_markerline(coords: list[tuple], svg_dwg: svgwrite.Drawing, linetype: str = "full"):
    if linetype == "dashed":
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=0.4,
                                        stroke_dasharray="3 5")
    elif linetype == "block":
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=0.6,
                                        stroke_dasharray="0.8 2.5")
    elif linetype == "point":
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=1.5)

    else:
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=0.4)

    svg_dwg.add(line)


def svg_add_point(geom: Point, prop: dict, svg_dwg: svgwrite.Drawing):
    coords = get_transformed_coords(geom)[0]
    for nr in prop['Rijstroken']:
        disp = (nr-1)*12
        square = svgwrite.shapes.Rect(insert=(coords[0]+disp, coords[1]), size=(10, 10), fill="black", stroke="red")
        svg_dwg.add(square)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000 * RATIO))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section['geometry'], section['properties'], dwg)

# MSIs
points = road.get_points()
for point in points:
    svg_add_point(point['geometry'], point['properties'], dwg)

# viewBox
dwg.viewbox(minx=TOP_LEFT_X, miny=TOP_LEFT_Y, width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisation finished successfully.")
