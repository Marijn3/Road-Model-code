from functions import *
import svgwrite
import math

LANE_WIDTH = 3.5

dfl = DataFrameLoader()
dfl.load_dataframes("A27")

road = RoadModel()
road.import_dataframes(dfl)

TOP_LEFT_X, TOP_LEFT_Y = get_coordinates(dfl.extent)[2]
BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y = get_coordinates(dfl.extent)[4]
VIEWBOX_WIDTH = abs(TOP_LEFT_X - BOTTOM_RIGHT_X)
VIEWBOX_HEIGHT = abs(TOP_LEFT_Y - BOTTOM_RIGHT_Y)
RATIO = VIEWBOX_HEIGHT / VIEWBOX_WIDTH


def get_road_color(n_lanes: int | float) -> str:
    # if 'Puntstuk' in prop.values():
    #     return 'dimgrey'

    if isinstance(n_lanes, float):
        return 'brown'

    return 'grey'


def get_n_lanes(prop: dict, only_main_lanes: bool = False) -> int | float:
    """
    Determines the number of lanes given road properties. It can be speficied
    whether only main lanes must be counted. The highest lane numbering will
    be returned.
    Args:
        prop (dict): Road properties to be evaluated.
        only_main_lanes: Boolean indicating whether only the main lanes should
            be considered. This includes 'rijstrook' and 'splitsing'.
    Returns:
        The number of (main) lanes, exluding 'puntstuk' registrations.
    """
    n_lanes = 0
    for lane_nr, lane_type in prop.items():
        if isinstance(lane_nr, int | float):
            if only_main_lanes:
                if lane_nr > n_lanes and lane_type in ['Rijstrook', 'Splitsing']:
                    n_lanes = lane_nr
            else:
                if lane_nr > n_lanes and lane_type not in ['Puntstuk']:
                    n_lanes = lane_nr
    return n_lanes


def get_transformed_coords(geom: LineString | Point) -> list[tuple]:
    """
    Flips geometries around the top border of the frame and returns the coordinates.
    This is necessary for visualisation, as the RD-coordinate system and the SVG
    coordinate system have a different definition of their y-axis.
    Args:
        geom (LineString or Point): Geometry to be flipped.
    Returns:
        List of coordinates making up the flipped geometry.
    """
    return [(coord[0], TOP_LEFT_Y - (coord[1] - TOP_LEFT_Y)) for coord in geom.coords]


def get_offset_coords(geom: LineString, offset: float) -> list[tuple]:
    """
    Offsets geometries by a given value and returns the coordinates.
    Also flips the geometries for visualisation.
    Args:
        geom (LineString or Point): Geometry to be flipped.
        offset (float): Amount of offset in meters. Positive offset
            is on the left side, seen in line direction.
    Returns:
        List of coordinates making up the offset geometry.
    """
    if offset == 0:
        return get_transformed_coords(geom)
    else:
        offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
        return get_transformed_coords(offset_geom)


def svg_add_section(section_data: dict, svg_dwg: svgwrite.Drawing):
    geom = section_data['geometry']
    prop = section_data['properties']

    n_lanes = get_n_lanes(prop)
    n_normal_lanes = get_n_lanes(prop, True)
    n_lanes_round = math.ceil(n_lanes)
    n_normal_lanes_round = math.ceil(n_normal_lanes)

    if n_lanes < 1:
        print(f"[WARNING:] Skipping visualisation of section without lanes: {section_data}")
        return

    # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
    offset = (LANE_WIDTH * n_normal_lanes_round) / 2 - LANE_WIDTH * n_lanes_round / 2
    asphalt_coords = get_offset_coords(geom, offset)

    width = LANE_WIDTH*n_lanes_round
    color = get_road_color(n_normal_lanes)

    asphalt = svgwrite.shapes.Polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width)
    svg_dwg.add(asphalt)

    add_separator_lines(geom, prop, n_lanes, n_normal_lanes, svg_dwg)


def add_separator_lines(geom: LineString, prop: dict, n_lanes: int, n_normal_lanes: int, svg_dwg: svgwrite.Drawing):
    n_lanes_round = math.ceil(n_lanes)
    n_normal_lanes_round = math.ceil(n_normal_lanes)

    # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
    offsets = [(LANE_WIDTH * n_normal_lanes_round) / 2 - LANE_WIDTH * i for i in range(n_lanes_round + 1)]

    # Add first line (left), except when the first lane is a vluchtstrook.
    line_coords = get_offset_coords(geom, offsets.pop(0))

    if prop[1] != 'Vluchtstrook':
        add_markerline(line_coords, svg_dwg)

    for lane_nr in range(1, n_lanes_round+1):
        line_coords = get_offset_coords(geom, offsets.pop(0))

        # To handle missing road numbers (due to taper/broadening/narrowing) temporarily. TODO: Remove this.
        if lane_nr not in prop.keys():
            continue

        # An emergency lane or rush hour lane (on the first lane) has a solid line.
        if prop[lane_nr] in ['Vluchtstrook', 'Spitsstrook']:
            add_markerline(line_coords, svg_dwg)
            continue

        # Stop when this is the final roadline (right).
        if lane_nr + 1 not in prop.keys():
            add_markerline(line_coords, svg_dwg)
            break

        # An emergency lane (not on the first lane) is always the final, rightmost lane.
        if prop[lane_nr + 1] == 'Vluchtstrook':
            add_markerline(line_coords, svg_dwg)
            break

        # A puntstuk is always the final, rightmost lane.
        if prop[lane_nr + 1] == 'Puntstuk':
            add_markerline(line_coords, svg_dwg, "point")
            break

        # All other lanes are separated by dashed lines.
        if prop[lane_nr] == prop[lane_nr + 1]:
            add_markerline(line_coords, svg_dwg, "dashed")
        # If the lane types are not the same, block markings are used.
        else:
            add_markerline(line_coords, svg_dwg, "block")


def add_markerline(coords: list[tuple], svg_dwg: svgwrite.Drawing, linetype: str = "full"):
    if linetype == "dashed":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.4,
                                        stroke_dasharray="3 5")
    elif linetype == "block":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.6,
                                        stroke_dasharray="0.8 2.5")
    elif linetype == "point":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=1.5)

    else:
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.4)

    svg_dwg.add(line)


# def svg_add_point(geom: Point, prop: dict, km: float, orientation: float, svg_dwg: svgwrite.Drawing):
def svg_add_point(point_data: dict, svg_dwg: svgwrite.Drawing):
    geom = point_data['geometry']
    prop = point_data['properties']
    km = point_data['km']

    coords = get_transformed_coords(geom)[0]
    if 'Rijstroken' in prop.keys():
        circle = svgwrite.shapes.Circle(center=coords, r=1.5, fill="black")
        svg_dwg.add(circle)
        for nr in prop['Rijstroken']:
            local_road_width = 3  # Replace with actual value
            size = 6
            displacement = (nr - 1) * (size*1.2) + local_road_width
            square = svgwrite.shapes.Rect(insert=(coords[0] + displacement, coords[1] - size/2), size=(size, size),
                                          fill="#1e1b17", stroke="black", stroke_width=0.3)
            svg_dwg.add(square)
        text = svgwrite.text.Text(km, insert=(coords[0] + displacement + size*1.2, coords[1] + 1.5),
                                  fill="white", font_family="Arial", font_size=4)
        svg_dwg.add(text)
    else:
        circle = svgwrite.shapes.Circle(center=coords, r=1.5, fill="black")
        svg_dwg.add(circle)
        # point_type = "H"  # prop.values()  # Extract the actual value there
        # text = svgwrite.text.Text(point_type, insert=(coords[0] + 2, coords[1] + 1),
        #                           fill="white", font_family="Arial", font_size=8)
        text = svgwrite.text.Text(km, insert=(coords[0] + 2, coords[1] + 1),  # transform="rotate(45)",
                                  fill="white", font_family="Arial", font_size=3)
        svg_dwg.add(text)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000 * RATIO))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Roads
sections = road.get_sections()
for section in sections:
    svg_add_section(section, dwg)

# MSIs
points = road.get_points()  # 'MSI'
for point in points:
    # orientation = road.get_local_orientation(point['geometry'])
    # svg_add_point(point['geometry'], point['properties'], point['km'], orientation, dwg)
    svg_add_point(point, dwg)

# viewBox
dwg.viewbox(minx=TOP_LEFT_X, miny=TOP_LEFT_Y, width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisation finished successfully.")
