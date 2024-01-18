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
    if 'Puntstuk' in prop.values():
        return 'dimgrey'

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
    return [(point[0], TOP_LEFT_Y - (point[1] - TOP_LEFT_Y)) for point in geom.coords]


def get_offset_coords(geom: LineString, offset: float) -> list[tuple]:
    if offset == 0:
        return [(coord[0], TOP_LEFT_Y - (coord[1] - TOP_LEFT_Y)) for coord in geom.coords]
    else:
        offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
        return [(coord[0], TOP_LEFT_Y - (coord[1] - TOP_LEFT_Y)) for coord in offset_geom.coords]


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

    # Offset centered around 0
    offsets = [LANE_WIDTH*i - (LANE_WIDTH*n_lanes)/2 for i in range(0, n_lanes+1)]

    for index, offset in enumerate(offsets):
        road_nr = index + 1
        line_coords = get_offset_coords(geom, offset)

        # Add first line (left).
        if road_nr == 1:
            print('first lane: solid')
            add_markerline(line_coords, svg_dwg)

        # Stop when this is the final roadline (right).
        if road_nr == n_lanes:
            print('final lane: solid. stop.')
            add_markerline(line_coords, svg_dwg)
            break

        if road_nr in prop:
            this_type = prop[road_nr]
        else:
            print('skip2')
            continue
        if road_nr + 1 in prop:
            next_type = prop[road_nr + 1]
        else:
            print('skip1')
            continue

        # An emergency lane is always the final, rightmost lane.
        if next_type == 'Vluchtstrook':
            print('vluchtstrook lane: solid. stop.')
            add_markerline(line_coords, svg_dwg)
            break

        # All other lanes are separated by dashed lines.
        if this_type == next_type:
            print('same types: dashed')
            add_markerline(line_coords, svg_dwg, "dashed")
        # If the lane types are not the same, block markings are used.
        else:
            print('different types: block')
            add_markerline(line_coords, svg_dwg, "block")


def add_markerline(coords: list[tuple], svg_dwg: svgwrite.Drawing, linetype: str = "full"):
    stroke = 0.4
    if linetype == "dashed":
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=stroke,
                                        stroke_dasharray="2.5")
    elif linetype == "block":
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=stroke,
                                        stroke_dasharray="0.4 1.5")
    else:
        line = svgwrite.shapes.Polyline(points=coords, stroke="white", fill="none", stroke_width=stroke)
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
