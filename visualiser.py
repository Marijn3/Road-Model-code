from functions import *
import svgwrite
import math

dfl = DataFrameLader("Vught")
wegmodel = WegModel(dfl)
netwerk = MSINetwerk(wegmodel)

# Visualiser parameters
LANE_WIDTH = 3.5
MSIBOX_SIZE = 5
VISUAL_PLAY = 1
C_TRANSPARENT = "#6D876D"
C_HIGHLIGHT = "brown"
C_ASPHALT = "grey"
C_WHITE = "#faf8f5"

TOP_LEFT_X, TOP_LEFT_Y = get_coordinates(dfl.extent)[2]
BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y = get_coordinates(dfl.extent)[4]
VIEWBOX_WIDTH = abs(TOP_LEFT_X - BOTTOM_RIGHT_X)
VIEWBOX_HEIGHT = abs(TOP_LEFT_Y - BOTTOM_RIGHT_Y)
RATIO = VIEWBOX_HEIGHT / VIEWBOX_WIDTH

# Dictionary to store squares by ID
element_by_id = {}


def get_road_color(prop: dict) -> str:
    """
    Determines color for road section visualisation based on the provided road properties.
    Args:
        prop (dict): Properties of road section.
    Returns:
        Color name as string.
    """
    if determine_gap(prop):
        return C_TRANSPARENT
    elif "Special" in prop.keys():
        return C_HIGHLIGHT
    else:
        return C_ASPHALT


def determine_gap(prop: dict) -> bool:
    """
    Determines whether there is a gap in the lane registrations of a section.
    Args:
        prop (dict): Properties of road section.
    Returns:
        Boolean indicating whether a gap occurs.
    """
    lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int) and lane not in ["Puntstuk"]])
    for lane_number in lane_numbers[:-1]:
        if lane_number + 1 not in prop.keys():
            return True
    return False


def get_flipped_coords(geom: LineString | Point) -> list[tuple]:
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


def get_offset_coords(geom: LineString, offset: float = 0) -> list[tuple]:
    """
    Offsets LineString geometries by a given value and returns the coordinates.
    Also flips the geometries for visualisation.
    Args:
        geom (LineString): Geometry to be flipped.
        offset (float): Amount of offset in meters. Positive offset
            is on the left side, seen in line direction.
    Returns:
        List of coordinates making up the offset geometry.
    """
    if offset == 0:
        return get_flipped_coords(geom)
    else:
        offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
        return get_flipped_coords(offset_geom)


def check_point_on_line(sid: int) -> None | dict:
    """
    Finds a *vergence point on the section. Assumes there is at most one *vergence
    point per section. In any case, the first one encountered is returned.
    Args:
        sid (int): Section ID to search for.
    Returns:

    """
    #
    for point_data in wegmodel.get_points_info():
        if sid in point_data["Verw_eigs"]["Sectie_ids"] and point_data["Obj_eigs"]["Type"] not in ["Signalering"]:
            return point_data
    return None


def get_changed_geometry(section_id: int, section_data: dict, point_data: dict) -> LineString:
    """
    Get the geometry of the section, where one of the endpoints is displaced if it overlaps with a
    *vergentiepunt point, and it is necessary to move it. Also adds a general property to the section
    that details whether there is a *vergence point at the start or end of it.
    Args:
        section_id (int): ID of section to be moved.
        section_data (dict): All data of the section to be moved.
        point_data (dict): Data of the point where the geometry should be moved.
    Returns:
        The geometry of the section, where one of the endpoints is displaced if necessary.
    """
    line_geom = section_data["Pos_eigs"]["Geometrie"]
    point_type = point_data["Obj_eigs"]["Type"]

    point_at_line_start = dwithin(Point(line_geom.coords[0]), point_data["Pos_eigs"]["Geometrie"], 0.5)
    point_at_line_end = dwithin(Point(line_geom.coords[-1]), point_data["Pos_eigs"]["Geometrie"], 0.5)

    # TODO: it may be possible that both the start and end of a section should be adjusted.
    if point_type == "Splitsing" and point_at_line_start:
        other_lane_id = [sid for sid in point_data["Verw_eigs"]["Uitgaande_secties"] if sid != section_id][0]
        change_start = True
    elif point_type == "Samenvoeging" and point_at_line_end:
        other_lane_id = [sid for sid in point_data["Verw_eigs"]["Ingaande_secties"] if sid != section_id][0]
        change_start = False
    elif point_type == "Uitvoeging" and point_at_line_start:
        other_lane_id = [sid for sid in point_data["Verw_eigs"]["Uitgaande_secties"] if sid != section_id][0]
        change_start = True
    elif point_type == "Invoeging" and point_at_line_end:
        other_lane_id = [sid for sid in point_data["Verw_eigs"]["Ingaande_secties"] if sid != section_id][0]
        change_start = False
    else:
        # This is for all cases where a section DOES connect to a *vergence point, but should not be moved.
        return line_geom

    other_section_data = wegmodel.sections[other_lane_id]
    return move_endpoint(section_data, other_section_data, point_data, change_start)


def move_endpoint(section_data: dict, other_section_data: dict, point_data: dict, change_start: bool = True):
    angle_radians = math.radians(point_data["Verw_eigs"]["Lokale_hoek"])
    tangent_vector = [-math.sin(angle_radians), math.cos(angle_radians)]  # Rotated by 90 degrees

    this_has_puntstuk = "Puntstuk" in section_data["Obj_eigs"].values()
    other_has_puntstuk = "Puntstuk" in other_section_data["Obj_eigs"].values()

    assert not (this_has_puntstuk and other_has_puntstuk),\
        f"Twee secties met puntstuk: {section_data}{other_section_data}"
    assert (this_has_puntstuk or other_has_puntstuk),\
        f"Geen sectie met puntstuk: {section_data}{other_section_data}"

    displacement = 0
    n_lanes_largest = point_data["Verw_eigs"]["Aantal_hoofdstroken"]

    if this_has_puntstuk:
        n_lanes_a, _ = wegmodel.get_n_lanes(section_data["Obj_eigs"])
        n_lanes_b, _ = wegmodel.get_n_lanes(other_section_data["Obj_eigs"])
        displacement = LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)

    if other_has_puntstuk:
        n_lanes_a, _ = wegmodel.get_n_lanes(other_section_data["Obj_eigs"])
        n_lanes_b, _ = wegmodel.get_n_lanes(section_data["Obj_eigs"])
        displacement = LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a) - LANE_WIDTH / 2 * (n_lanes_a + n_lanes_b)

    line_geom = section_data["Pos_eigs"]["Geometrie"]
    if change_start:
        point_to_displace = line_geom.coords[0]
    else:
        point_to_displace = line_geom.coords[-1]

    displaced_point = Point(point_to_displace[0] + tangent_vector[0] * displacement,
                            point_to_displace[1] + tangent_vector[1] * displacement)

    if change_start:
        return LineString([displaced_point.coords[0]] + [coord for coord in line_geom.coords[1:]])
    else:
        return LineString([coord for coord in line_geom.coords[:-1]] + [displaced_point.coords[0]])


def svg_add_section(section_id: int, section_data: dict, svg_dwg: svgwrite.Drawing):
    point_on_line = check_point_on_line(section_id)

    if point_on_line:
        geom = get_changed_geometry(section_id, section_data, point_on_line)
    else:
        geom = section_data["Pos_eigs"]["Geometrie"]

    n_main_lanes, n_total_lanes = wegmodel.get_n_lanes(section_data["Obj_eigs"])

    if n_main_lanes < 1 or n_total_lanes < 1:
        # These sections are not added. They fall outside the visualisation frame.
        return

    # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
    offset = (LANE_WIDTH * n_main_lanes) / 2 - LANE_WIDTH * n_total_lanes / 2

    asphalt_coords = get_offset_coords(geom, offset)
    color = get_road_color(section_data["Obj_eigs"])
    width = LANE_WIDTH * n_total_lanes

    asphalt = svgwrite.shapes.Polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width)
    svg_dwg.add(asphalt)

    should_have_marking = color in [C_ASPHALT, C_HIGHLIGHT]

    if should_have_marking:
        add_lane_marking(geom, section_data, n_main_lanes, svg_dwg)


def add_lane_marking(geom: LineString, section_data: dict, n_main_lanes: int, svg_dwg: svgwrite.Drawing):
    prop = section_data["Obj_eigs"]
    lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int)])

    # Offset centered around main lanes. Positive offset distance is on the left side of the LineString.
    marking_offsets = [(LANE_WIDTH * n_main_lanes) / 2 - LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

    first_lane_nr = lane_numbers[0]
    last_lane_nr = lane_numbers[-1]

    # Add first solid marking (leftmost), except when the first lane is a vluchtstrook.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[first_lane_nr] != "Vluchtstrook":
        add_markerline(line_coords, svg_dwg)

    # Add middle markings. All of these markings have a this_lane and a next_lane
    for lane_number in lane_numbers[:-1]:
        this_lane = prop[lane_number]
        next_lane = prop[lane_number + 1]
        line_coords = get_offset_coords(geom, marking_offsets.pop(0))

        # A puntstuk is the final lane.
        if next_lane == "Puntstuk":
            if section_data["Verw_eigs"]["*vergentiepunt_start"]:
                add_markerline(line_coords, svg_dwg, "Punt_start")
            elif section_data["Verw_eigs"]["*vergentiepunt_einde"]:
                add_markerline(line_coords, svg_dwg, "Punt_einde")
            # else:
                # print(f"not found in keys of {section_data}")
            break

        # An emergency lane is demarcated with a solid line.
        if this_lane == "Vluchtstrook" or next_lane == "Vluchtstrook":
            add_markerline(line_coords, svg_dwg)

        # A plus lane is demarcated with a 9-3 dashed line.
        elif this_lane == "Plusstrook":
            add_markerline(line_coords, svg_dwg, "Streep-9-3")

        # If the next lane is a samenvoeging, use normal dashed lane marking.
        elif next_lane == "Samenvoeging":
            add_markerline(line_coords, svg_dwg, "Streep-3-9")

        # A rush hour lane (on the final lane) has special lines.
        elif next_lane == "Spitsstrook" and lane_number + 1 == last_lane_nr:
            add_markerline(line_coords, svg_dwg)

        # All other lanes are separated by dashed lines.
        elif this_lane == next_lane:
            add_markerline(line_coords, svg_dwg, "Streep-3-9")

        # If the lane types are not the same, block markings are used.
        else:
            add_markerline(line_coords, svg_dwg, "Blok")

    # Add last solid marking (rightmost), except when the last lane is a vluchtstrook or puntstuk.
    # Spitsstrook has special lane marking.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[last_lane_nr] == "Spitsstrook":
        add_markerline(line_coords, svg_dwg, "Dun")
    elif prop[last_lane_nr] not in ["Vluchtstrook", "Puntstuk"]:
        add_markerline(line_coords, svg_dwg)


def add_markerline(coords: list[tuple], svg_dwg: svgwrite.Drawing, linetype: str = "full"):
    if linetype == "Streep-3-9":
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4,
                                        stroke_dasharray="3 9")
    elif linetype == "Streep-9-3":
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4,
                                        stroke_dasharray="9 3")
    elif linetype == "Blok":
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.6,
                                        stroke_dasharray="0.8 4")
    elif linetype == "Punt_start" or linetype == "Punt_einde":
        triangle_end = coords[-1] if linetype == "Punt_start" else coords[0]

        vec = [coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]]
        mag = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        third_point = (triangle_end[0] + LANE_WIDTH * -vec[1] / mag, triangle_end[1] + LANE_WIDTH * vec[0] / mag)
        all_points = coords + [third_point]

        triangle = svgwrite.shapes.Polygon(points=all_points, fill=C_WHITE)
        svg_dwg.add(triangle)

        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4)

    elif linetype == "Dun":
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.2)

    else:
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4)

    svg_dwg.add(line)


def svg_add_point(point_data: dict, svg_dwg: svgwrite.Drawing):
    coords = get_flipped_coords(point_data["Pos_eigs"]["Geometrie"])[0]
    info_offset = LANE_WIDTH * (point_data["Verw_eigs"]["Aantal_stroken"] + (point_data["Verw_eigs"]["Aantal_stroken"] - point_data["Verw_eigs"]["Aantal_hoofdstroken"])) / 2
    rotate_angle = 90 - point_data["Verw_eigs"]["Lokale_hoek"]

    if point_data["Obj_eigs"]["Type"] == "Signalering":
        # display_MSI_roadside(point_data, coords, info_offset, rotate_angle, svg_dwg)
        display_MSI_onroad(point_data, coords, info_offset, rotate_angle, svg_dwg)
    else:
        display_vergence(point_data, coords, info_offset, rotate_angle, svg_dwg)


def display_MSI_roadside(point_data: dict, coords: tuple, info_offset: float, rotate_angle: float, svg_dwg: svgwrite.Drawing):
    group_msi_row = svgwrite.container.Group()

    for nr in point_data["Obj_eigs"]["Rijstrooknummers"]:
        msi_name = make_name(point_data, nr)
        displacement = info_offset + VISUAL_PLAY + (nr - 1) * (VISUAL_PLAY + MSIBOX_SIZE)
        square = svgwrite.shapes.Rect(id=msi_name,
                                      insert=(coords[0] + displacement, coords[1] - MSIBOX_SIZE / 2),
                                      size=(MSIBOX_SIZE, MSIBOX_SIZE),
                                      fill="#1e1b17", stroke="black", stroke_width=0.3,
                                      onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                                      onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
        group_msi_row.add(square)
        element_by_id[msi_name] = square, rotate_angle, coords

    text = svgwrite.text.Text(make_text_hecto(point_data["Pos_eigs"]["Km"], point_data["Pos_eigs"]["Hectoletter"]),
                              insert=(coords[0] + displacement + MSIBOX_SIZE * 1.2, coords[1] + 1.5),
                              fill="white", font_family="Arial", font_size=4)

    group_msi_row.add(text)
    group_msi_row.rotate(rotate_angle, center=coords)
    svg_dwg.add(group_msi_row)


def display_MSI_onroad(point_data: dict, coords: tuple, info_offset: float, rotate_angle: float, svg_dwg: svgwrite.Drawing):
    group_msi_row = svgwrite.container.Group()
    box_size = LANE_WIDTH*0.8
    play = (LANE_WIDTH - box_size)/2

    for nr in point_data["Obj_eigs"]["Rijstrooknummers"]:
        msi_name = make_name(point_data, nr)
        displacement = LANE_WIDTH * (nr - 1) - point_data["Verw_eigs"]["Aantal_hoofdstroken"] * LANE_WIDTH / 2
        square = svgwrite.shapes.Rect(id=msi_name,
                                      insert=(coords[0] + displacement + play, coords[1] - box_size / 2),
                                      size=(box_size, box_size),
                                      fill="#1e1b17", stroke="black", stroke_width=0.3,
                                      onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                                      onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
        group_msi_row.add(square)
        element_by_id[msi_name] = square, rotate_angle, coords

    text = svgwrite.text.Text(make_text_hecto(point_data["Pos_eigs"]["Km"], point_data["Pos_eigs"]["Hectoletter"]),
                              insert=(coords[0] + VISUAL_PLAY + info_offset, coords[1] + 1.1),
                              fill="white", font_family="Arial", font_size=3)

    group_msi_row.add(text)
    group_msi_row.rotate(rotate_angle, center=coords)
    svg_dwg.add(group_msi_row)


def display_vergence(point_data: dict, coords: tuple, info_offset: float, rotate_angle: float, svg_dwg: svgwrite.Drawing):
    group_vergence = svgwrite.container.Group()

    text = svgwrite.text.Text(f"{point_data['Pos_eigs']['Km']} {point_data['Obj_eigs']['Type']}",
                              insert=(coords[0] + VISUAL_PLAY + info_offset, coords[1] + 1),
                              fill="white", font_family="Arial", font_size=3)

    group_vergence.add(text)
    group_vergence.rotate(rotate_angle, center=coords)
    svg_dwg.add(group_vergence)


def draw_msi_relations(svg_dwg: svgwrite.Drawing):
    # Draw primary relations
    for element_id in element_by_id.keys():
        start_element, start_rotation, start_origin = element_by_id.get(element_id)
        start_pos = get_center_coords(start_element, start_rotation, start_origin)
        for row in netwerk.MSIrows:
            for msi in row.MSIs.values():
                if msi.name == element_id:
                    if msi.properties["d"]:
                        end_element, end_rotation, end_origin = element_by_id.get(msi.properties["d"])
                        end_pos = get_center_coords(end_element, end_rotation, end_origin)
                        draw_primary(start_pos, end_pos, svg_dwg)
                    if msi.properties["ds"]:
                        for end_id in msi.properties["ds"]:
                            end_element, end_rotation, end_origin = element_by_id.get(end_id)
                            end_pos = get_center_coords(end_element, end_rotation, end_origin)
                            draw_secondary(start_pos, end_pos, svg_dwg)


def draw_primary(start_pos: tuple, end_pos: tuple, svg_dwg: svgwrite.Drawing):
    svg_dwg.add(svgwrite.shapes.Line(start=start_pos, end=end_pos, stroke="cyan", stroke_width=0.4))
    svg_dwg.add(svgwrite.shapes.Circle(center=start_pos, r=0.75, fill="cyan"))
    svg_dwg.add(svgwrite.shapes.Circle(center=end_pos, r=0.75, fill="cyan"))


def draw_secondary(start_pos: tuple, end_pos: tuple, svg_dwg: svgwrite.Drawing):
    svg_dwg.add(svgwrite.shapes.Line(start=start_pos, end=end_pos, stroke="magenta", stroke_width=0.4))
    svg_dwg.add(svgwrite.shapes.Circle(center=start_pos, r=0.75, fill="magenta"))
    svg_dwg.add(svgwrite.shapes.Circle(center=end_pos, r=0.75, fill="magenta"))


def get_center_coords(element, angle_degrees, origin):
    x = element.attribs["x"] + element.attribs["width"] / 2
    y = element.attribs["y"] + element.attribs["height"] / 2
    return rotate_point((x, y), origin, angle_degrees)


def rotate_point(draw_point, origin, angle_degrees):
    angle_rad = math.radians(angle_degrees)
    x, y = draw_point
    ox, oy = origin
    qx = ox + math.cos(angle_rad) * (x - ox) - math.sin(angle_rad) * (y - oy)
    qy = oy + math.sin(angle_rad) * (x - ox) + math.cos(angle_rad) * (y - oy)
    return qx, qy


def make_name(point_data, nr) -> str:
    if point_data["Pos_eigs"]["Hectoletter"]:
        return f"{point_data['Pos_eigs']['Wegnummer']}_{point_data['Pos_eigs']['Hectoletter'].upper()}:{point_data['Pos_eigs']['Km']}:{nr}"
    else:
        return f"{point_data['Pos_eigs']['Wegnummer']}{point_data['Pos_eigs']['Rijrichting']}:{point_data['Pos_eigs']['Km']}:{nr}"


def make_text_hecto(km: float, letter: str | None) -> str:
    if letter:
        return f"{km} {letter}"
    return f"{km}"


# Create SVG drawing
dwg = svgwrite.Drawing(filename="Server/Data/road_visualization.svg", size=(1000, 1000 * RATIO))

# Background
dwg.add(svgwrite.shapes.Rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Section data (roads)
print("Sectiedata visualiseren...")
for section_id, section_info in wegmodel.sections.items():
    svg_add_section(section_id, section_info, dwg)

# Point data (MSIs, convergence, divergence)
print("Puntdata visualiseren...")
points = wegmodel.get_points_info()
for point in points:
    svg_add_point(point, dwg)

# MSI relations
print("MSI-relaties visualiseren...")
draw_msi_relations(dwg)

# viewBox
dwg.viewbox(minx=TOP_LEFT_X, miny=TOP_LEFT_Y, width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT)

# Save SVG file
dwg.save(pretty=True, indent=2)

print("Visualisatie succesvol afgerond.")
