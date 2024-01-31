from functions import *
import svgwrite
import math

LANE_WIDTH = 3.5

dfl = DataFrameLoader("Vught")
roadmodel = RoadModel(dfl)

TOP_LEFT_X, TOP_LEFT_Y = get_coordinates(dfl.extent)[2]
BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y = get_coordinates(dfl.extent)[4]
VIEWBOX_WIDTH = abs(TOP_LEFT_X - BOTTOM_RIGHT_X)
VIEWBOX_HEIGHT = abs(TOP_LEFT_Y - BOTTOM_RIGHT_Y)
RATIO = VIEWBOX_HEIGHT / VIEWBOX_WIDTH


def get_road_color(prop: dict) -> str:
    # if 'Puntstuk' in prop.values():
    #     return 'dimgrey'

    lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int) and lane not in ['Puntstuk']])
    for lane_number in lane_numbers[:-1]:
        if lane_number + 1 not in prop.keys():
            return 'orange'

    if 'Special' in prop.keys():
        return 'brown'

    return 'grey'


def get_n_lanes(prop: dict) -> tuple[int, int]:
    """
    Determines the number of lanes given road properties.
    Args:
        prop (dict): Road properties to be evaluated.
    Returns:
        1) The number of main lanes - only 'Rijstrook', 'Splitsing' and 'Samenvoeging' registrations.
        2) The number of lanes, exluding 'puntstuk' registrations.
    """
    main_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                  and lane_type in ['Rijstrook', 'Splitsing', 'Samenvoeging']]
    any_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                 and lane_type not in ['Puntstuk']]
    return len(main_lanes), len(any_lanes)


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


def check_point_on_line(section_id: int) -> None | dict:
    for point_data in roadmodel.get_points():
        if section_id in point_data['section_ids'] and point_data['properties']['Type'] not in ['Signalering']:
            print(f"There is a *vergence point ({point_data['km']}, {point_data['geometry']}, "
                  f"{point_data['properties']['Type']}) on section {section_id}")
            return point_data
    return None


def change_geom(section_data: dict, point_data: dict):
    line_geom = section_data['geometry']
    point_type = point_data['properties']['Type']
    point_geom = point_data['geometry']
    point_angle = point_data['properties']['Local angle']

    first_point = Point(line_geom.coords[0])
    last_point = Point(line_geom.coords[-1])

    point_at_line_start = dwithin(first_point, point_geom, 0.5)
    point_at_line_end = dwithin(last_point, point_geom, 0.5)
    has_puntstuk = 'Puntstuk' in section_data['properties'].values()

    if point_type == 'D' and point_at_line_start:
        print(f"two geometries should be changed for {point_geom}: one of which is {section_data}")
        changed_geom = line_geom  # TODO: TEMP

    elif point_type == 'C' and point_at_line_end:
        print(f"two geometries should be changed for {point_geom}: one of which is {section_data}")
        changed_geom = line_geom  # TODO: TEMP

    elif point_type == 'U' and point_at_line_start and not has_puntstuk:
        print(f"one geometry should be changed: {section_data}")
        print(line_geom)
        angle = 90 - point_angle
        print("1)", first_point)

        angle_radians = math.radians(angle)

        x_component = math.cos(angle_radians)
        y_component = math.sin(angle_radians)
        vector = [x_component, y_component]
        x = first_point.x
        y = first_point.y
        if section_data['roadside'] == "L":
            displacement = 7
        else:
            displacement = -8.75
        displaced_point = Point(x + vector[0]*displacement, y + vector[1]*displacement)
        print("2)", displaced_point)
        changed_geom = [coord for coord in line_geom.coords]
        changed_geom[0] = displaced_point.coords[0]
        changed_geom = LineString(changed_geom)
        print(changed_geom)

    elif point_type == 'I' and point_at_line_end and not has_puntstuk:
        print(f"one geometry should be changed: {section_data}")
        changed_geom = line_geom  # TODO: TEMP

    else:
        print(f"It will be left alone, because {section_data}")
        changed_geom = line_geom

    return changed_geom


def svg_add_section(section_id: int, section_data: dict, svg_dwg: svgwrite.Drawing):
    point_on_line = check_point_on_line(section_id)

    if point_on_line:
        geom = change_geom(section_data, point_on_line)
    else:
        geom = section_data['geometry']

    prop = section_data['properties']

    n_main_lanes, n_total_lanes = get_n_lanes(prop)

    if n_total_lanes < 1:
        print(f"[WARNING:] Skipping visualisation of section without any lanes: {section_data}")
        return
    if n_main_lanes < 1:
        print(f"[WARNING:] Skipping visualisation of section without main lanes: {section_data}")
        return

    # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
    offset = (LANE_WIDTH * n_main_lanes) / 2 - LANE_WIDTH * n_total_lanes / 2

    asphalt_coords = get_offset_coords(geom, offset)
    color = get_road_color(prop)
    width = LANE_WIDTH * n_total_lanes

    asphalt = svgwrite.shapes.Polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width)
    svg_dwg.add(asphalt)

    if color not in ['orange']:
        add_separator_lines(geom, prop, n_total_lanes, n_main_lanes, svg_dwg)


def add_separator_lines(geom: LineString, prop: dict, n_total_lanes: int, n_main_lanes: int, svg_dwg: svgwrite.Drawing):
    lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int)])

    # Offset centered around main lanes. Positive offset distance is on the left side of the line.
    marking_offsets = [(LANE_WIDTH * n_main_lanes) / 2 - LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

    first_lane_nr = lane_numbers[0]
    last_lane_nr = lane_numbers[-1]

    # Add first solid line (leftmost), except when the first lane is a vluchtstrook.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[first_lane_nr] != 'Vluchtstrook':
        add_markerline(line_coords, svg_dwg)

    for lane_number in lane_numbers[:-1]:
        this_lane = prop[lane_number]
        next_lane = prop[lane_number + 1]
        line_coords = get_offset_coords(geom, marking_offsets.pop(0))

        # A puntstuk is the final lane.
        if next_lane == 'Puntstuk':
            add_markerline(line_coords, svg_dwg, "point")
            break

        # An emergency lane is demarcated with a solid line.
        if this_lane == 'Vluchtstrook' or next_lane == 'Vluchtstrook':
            add_markerline(line_coords, svg_dwg)

        # A plus lane is demarcated with a 9-3 dashed line.
        elif this_lane == 'Plusstrook':
            add_markerline(line_coords, svg_dwg, "dashed-9-3")

        # If the next lane is a samenvoeging, use normal dashed lane marking.
        elif next_lane == 'Samenvoeging':
            add_markerline(line_coords, svg_dwg, "dashed-3-9")

        # A rush hour lane (on the final lane) has special lines.
        elif next_lane == 'Spitsstrook' and lane_number + 1 == last_lane_nr:
            add_markerline(line_coords, svg_dwg)

        # All other lanes are separated by dashed lines.
        elif this_lane == next_lane:
            add_markerline(line_coords, svg_dwg, "dashed-3-9")

        # If the lane types are not the same, block markings are used.
        else:
            add_markerline(line_coords, svg_dwg, "block")

    # Add last solid line (rightmost), except when the last lane is a vluchtstrook or puntstuk.
    # Spitsstrook has special lining.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[last_lane_nr] == 'Spitsstrook':
        add_markerline(line_coords, svg_dwg, "thin")
    elif prop[last_lane_nr] not in ['Vluchtstrook', 'Puntstuk']:
        add_markerline(line_coords, svg_dwg)


def add_markerline(coords: list[tuple], svg_dwg: svgwrite.Drawing, linetype: str = "full"):
    if linetype == "dashed-3-9":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.4,
                                        stroke_dasharray="3 9")
    elif linetype == "dashed-9-3":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.4,
                                        stroke_dasharray="9 3")
    elif linetype == "block":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.6,
                                        stroke_dasharray="0.8 4")
    elif linetype == "point":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=1.5)

    elif linetype == "thin":
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.2)

    else:
        line = svgwrite.shapes.Polyline(points=coords, stroke="#faf8f5", fill="none", stroke_width=0.4)

    svg_dwg.add(line)


def svg_add_point(point_data: dict, svg_dwg: svgwrite.Drawing):
    geom = point_data['geometry']
    prop = point_data['properties']
    km = point_data['km']

    angle = prop['Local angle']
    rotate_angle = 90 - angle
    msibox_size = 6
    play = 1.2
    info_offset = LANE_WIDTH * (prop['nTotalLanes'] + (prop['nTotalLanes'] - prop['nMainLanes'])) / 2

    coords = get_transformed_coords(geom)[0]
    if prop['Type'] == 'Signalering':
        group_msi_row = svgwrite.container.Group()
        circle = svgwrite.shapes.Circle(center=coords, r=1.5, fill="black")
        group_msi_row.add(circle)

        for nr in prop['Rijstroken']:
            displacement = info_offset + play + (nr - 1) * (play + msibox_size)
            square = svgwrite.shapes.Rect(insert=(coords[0] + displacement, coords[1] - msibox_size/2),
                                          size=(msibox_size, msibox_size),
                                          fill="#1e1b17", stroke="black", stroke_width=0.3)
            group_msi_row.add(square)
        text = svgwrite.text.Text(km,
                                  insert=(coords[0] + displacement + msibox_size*1.2, coords[1] + 1.5),
                                  fill="white", font_family="Arial", font_size=4)
        group_msi_row.add(text)
        group_msi_row.rotate(rotate_angle, center=coords)
        svg_dwg.add(group_msi_row)
    else:
        group_vergence = svgwrite.container.Group()
        circle = svgwrite.shapes.Circle(center=coords, r=1.5, fill="black")
        group_vergence.add(circle)
        point_type = [type_letter for type_letter in prop.values()][0]
        text = svgwrite.text.Text(point_type + " " + str(km),
                                  insert=(coords[0] + play + info_offset, coords[1] + 1),
                                  fill="white", font_family="Arial", font_size=3)
        group_vergence.add(text)
        group_vergence.rotate(rotate_angle, center=coords)
        svg_dwg.add(group_vergence)


# Create SVG drawing
dwg = svgwrite.Drawing(filename="roadvis.svg", size=(1000, 1000 * RATIO))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Section data (roads)
for section_id, section in roadmodel.sections.items():
    svg_add_section(section_id, section, dwg)

# Point data (MSIs, convergence, divergence)
points = roadmodel.get_points()  # 'MSI'
for point in points:
    svg_add_point(point, dwg)

# viewBox
dwg.viewbox(minx=TOP_LEFT_X, miny=TOP_LEFT_Y, width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisation finished successfully.")
