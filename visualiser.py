from functions import *
import svgwrite
import math

dfl = DataFrameLader("Vught")
# Gedefinieerde locaties: [Volledig correcte import] Vught, Oosterhout, Goirle, Vinkeveen
#                         [Verwerkingsfouten] Zonzeel, Zuidasdok [Puntstuk registrations]
#                         [Importfouten] A2VK, Bavel, Everdingen
# dfl = DataFrameLader({"noord": 484000, "oost": 120200, "zuid": 483000, "west": 117000})

wegmodel = WegModel(dfl)
netwerk = MSINetwerk(wegmodel, maximale_zoekafstand=2000, alle_secundaire_relaties=True)

# Visualiser parameters
LANE_WIDTH = 3.5
MSIBOX_SIZE = 20
DISPLAY_ONROAD = False

if DISPLAY_ONROAD:
    MSIBOX_SIZE = LANE_WIDTH*0.8
    TEXT_SIZE = MSIBOX_SIZE*0.8
    VISUAL_PLAY = MSIBOX_SIZE*0.2
    STROKE = MSIBOX_SIZE*0.07
else:
    TEXT_SIZE = MSIBOX_SIZE*0.6
    VISUAL_PLAY = MSIBOX_SIZE*0.2
    STROKE = MSIBOX_SIZE*0.05

C_TRANSPARENT = "#6D876D"
C_HIGHLIGHT = "dimgrey"
C_ASPHALT = "grey"
C_WHITE = "#faf8f5"

TOP_LEFT_X, TOP_LEFT_Y = get_coordinates(dfl.extent)[2]
BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y = get_coordinates(dfl.extent)[4]
VIEWBOX_WIDTH = abs(TOP_LEFT_X - BOTTOM_RIGHT_X)
VIEWBOX_HEIGHT = abs(TOP_LEFT_Y - BOTTOM_RIGHT_Y)
RATIO = VIEWBOX_HEIGHT / VIEWBOX_WIDTH

COLORMAP = {
    "p": "cyan",     # Primary
    "s": "magenta",  # Secondary
    "t": "red",      # Taper
    "b": "orange",   # Broadening
    "n": "yellow",   # Narrowing
}

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


def check_point_on_line(sid: int) -> None | ObjectInfo:
    """
    Finds a *vergence point on the section. Assumes there is at most one *vergence
    point per section. In any case, the first one encountered is returned.
    Args:
        sid (int): Section ID to search for.
    Returns:

    """
    #
    for point_info in wegmodel.get_points_info():
        if sid in point_info.verw_eigs.sectie_ids and point_info.obj_eigs["Type"] not in ["Signalering"]:
            return point_info
    return None


def get_changed_geometry(section_id: int, section_info: ObjectInfo, point_info: ObjectInfo) -> LineString:
    """
    Get the geometry of the section, where one of the endpoints is displaced if it overlaps with a
    *vergentiepunt point, and it is necessary to move it. Also adds a general property to the section
    that details whether there is a *vergence point at the start or end of it.
    Args:
        section_id (int): ID of section to be moved.
        section_info (ObjectInfo): All data of the section to be moved.
        point_info (ObjectINfo): Data of the point where the geometry should be moved.
    Returns:
        The geometry of the section, where one of the endpoints is displaced if necessary.
    """
    line_geom = section_info.pos_eigs.geometrie
    point_type = point_info.obj_eigs["Type"]

    point_is_at_line_start = dwithin(Point(line_geom.coords[0]), point_info.pos_eigs.geometrie, 0.5)
    point_is_at_line_end = dwithin(Point(line_geom.coords[-1]), point_info.pos_eigs.geometrie, 0.5)

    # TODO: it may be possible that both the start and end of a section should be adjusted.
    if point_type == "Splitsing" and point_is_at_line_start:
        other_lane_id = [sid for sid in point_info.verw_eigs.uitgaande_secties if sid != section_id][0]
        change_start = True
    elif point_type == "Samenvoeging" and point_is_at_line_end:
        other_lane_id = [sid for sid in point_info.verw_eigs.ingaande_secties if sid != section_id][0]
        change_start = False
    elif point_type == "Uitvoeging" and point_is_at_line_start:
        other_lane_id = [sid for sid in point_info.verw_eigs.uitgaande_secties if sid != section_id][0]
        change_start = True
    elif point_type == "Invoeging" and point_is_at_line_end:
        other_lane_id = [sid for sid in point_info.verw_eigs.ingaande_secties if sid != section_id][0]
        change_start = False
    else:
        # This is for all cases where a section DOES connect to a *vergence point, but should not be moved.
        return line_geom

    other_section_data = wegmodel.sections[other_lane_id]
    return move_endpoint(section_info, other_section_data, point_info, change_start)


def move_endpoint(section_info: ObjectInfo, other_section_info: ObjectInfo,
                  point_info: ObjectInfo, change_start: bool = True):
    angle_radians = math.radians(point_info.verw_eigs.lokale_hoek)
    tangent_vector = [-math.sin(angle_radians), math.cos(angle_radians)]  # Rotated by 90 degrees

    this_has_puntstuk = "Puntstuk" in section_info.obj_eigs.values()
    other_has_puntstuk = "Puntstuk" in other_section_info.obj_eigs.values()

    assert not (this_has_puntstuk and other_has_puntstuk),\
        f"Twee secties met puntstuk bij {point_info.pos_eigs}\n{section_info}\n{other_section_info}"
    assert (this_has_puntstuk or other_has_puntstuk),\
        f"Geen sectie met puntstuk bij {point_info.pos_eigs}\n{section_info}\n{other_section_info}"

    displacement = 0
    n_lanes_largest = point_info.verw_eigs.aantal_hoofdstroken

    if this_has_puntstuk:
        n_lanes_a, _ = wegmodel.get_n_lanes(section_info.obj_eigs)
        n_lanes_b, _ = wegmodel.get_n_lanes(other_section_info.obj_eigs)
        displacement = LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)

    if other_has_puntstuk:
        n_lanes_a, _ = wegmodel.get_n_lanes(other_section_info.obj_eigs)
        n_lanes_b, _ = wegmodel.get_n_lanes(section_info.obj_eigs)
        displacement = LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a) - LANE_WIDTH / 2 * (n_lanes_a + n_lanes_b)

    line_geom = section_info.pos_eigs.geometrie
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


def svg_add_section(section_id: int, section_info: ObjectInfo, dwg: svgwrite.Drawing):
    point_on_line = check_point_on_line(section_id)

    if point_on_line:
        geom = get_changed_geometry(section_id, section_info, point_on_line)
    else:
        geom = section_info.pos_eigs.geometrie

    n_main_lanes, n_total_lanes = wegmodel.get_n_lanes(section_info.obj_eigs)

    n_main_lanes = section_info.verw_eigs.aantal_hoofdrijstroken
    n_lanes_left = section_info.verw_eigs.aantal_rijstroken_links
    n_lanes_right = section_info.verw_eigs.aantal_rijstroken_rechts

    if n_main_lanes < 1 or n_total_lanes < 1:
        # These sections are not added. This is fine, because they fall outside the visualisation frame.
        return

    # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
    offset = LANE_WIDTH * (n_lanes_left - n_lanes_right) / 2

    asphalt_coords = get_offset_coords(geom, offset)
    color = get_road_color(section_info.obj_eigs)
    width = LANE_WIDTH * n_total_lanes

    asphalt = svgwrite.shapes.Polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width)
    dwg.add(asphalt)

    should_have_marking = color in [C_ASPHALT, C_HIGHLIGHT]

    if should_have_marking:
        add_lane_marking(geom, section_info, dwg)


def add_lane_marking(geom: LineString, section_info: ObjectInfo, dwg: svgwrite.Drawing):
    prop = section_info.obj_eigs
    lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int)])

    # Offset centered around main lanes. Positive offset distance is on the left side of the LineString.
    marking_offsets = [(LANE_WIDTH * section_info.verw_eigs.aantal_hoofdrijstroken) / 2
                       + LANE_WIDTH * section_info.verw_eigs.aantal_rijstroken_links
                       - LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

    first_lane_nr = lane_numbers[0]
    last_lane_nr = lane_numbers[-1]

    # Add first solid marking (leftmost), except when the first lane is a vluchtstrook.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[first_lane_nr] != "Vluchtstrook":
        add_markerline(line_coords, dwg)

    # Add middle markings. All of these markings have a this_lane and a next_lane
    for lane_number in lane_numbers[:-1]:
        this_lane = prop[lane_number]
        next_lane = prop[lane_number + 1]
        line_coords = get_offset_coords(geom, marking_offsets.pop(0))

        # A puntstuk is the final lane.
        if next_lane == "Puntstuk":
            if section_info.verw_eigs.vergentiepunt_start:
                add_markerline(line_coords, dwg, "Punt_start")
            elif section_info.verw_eigs.vergentiepunt_einde:
                add_markerline(line_coords, dwg, "Punt_einde")
            # else:
                # print(f"not found in keys of {section_data}")
            break

        # An emergency lane is demarcated with a solid line.
        if this_lane == "Vluchtstrook" or next_lane == "Vluchtstrook":
            add_markerline(line_coords, dwg)

        # A plus lane is demarcated with a 9-3 dashed line.
        elif this_lane == "Plusstrook":
            add_markerline(line_coords, dwg, "Streep-9-3")

        # If the next lane is a samenvoeging, use normal dashed lane marking.
        elif next_lane == "Samenvoeging":
            add_markerline(line_coords, dwg, "Streep-3-9")

        # A rush hour lane (on the final lane) has special lines.
        elif next_lane == "Spitsstrook" and lane_number + 1 == last_lane_nr:
            add_markerline(line_coords, dwg)

        # All other lanes are separated by dashed lines.
        elif this_lane == next_lane:
            add_markerline(line_coords, dwg, "Streep-3-9")

        # If the lane types are not the same, block markings are used.
        else:
            add_markerline(line_coords, dwg, "Blok")

    # Add last solid marking (rightmost), except when the last lane is a vluchtstrook or puntstuk.
    # Spitsstrook has special lane marking.
    line_coords = get_offset_coords(geom, marking_offsets.pop(0))
    if prop[last_lane_nr] == "Spitsstrook":
        add_markerline(line_coords, dwg, "Dun")
    elif prop[last_lane_nr] not in ["Vluchtstrook", "Puntstuk"]:
        add_markerline(line_coords, dwg)


def add_markerline(coords: list[tuple], dwg: svgwrite.Drawing, linetype: str = "full"):
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
        dwg.add(triangle)

        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4)

    elif linetype == "Dun":
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.2)

    else:
        line = svgwrite.shapes.Polyline(points=coords, fill="none", stroke=C_WHITE, stroke_width=0.4)

    dwg.add(line)


def svg_add_point(point_info: ObjectInfo, dwg: svgwrite.Drawing):
    coords = get_flipped_coords(point_info.pos_eigs.geometrie)[0]
    info_offset = LANE_WIDTH * (point_info.verw_eigs.aantal_stroken +
                                (point_info.verw_eigs.aantal_stroken - point_info.verw_eigs.aantal_hoofdstroken)) / 2
    rotate_angle = 90 - point_info.verw_eigs.lokale_hoek

    if point_info.obj_eigs["Type"] == "Signalering":
        if DISPLAY_ONROAD:
            display_MSI_onroad(point_info, coords, info_offset, rotate_angle, dwg)
        else:
            display_MSI_roadside(point_info, coords, info_offset, rotate_angle, dwg)
    else:
        display_vergence(point_info, coords, info_offset, rotate_angle, dwg)


def display_MSI_roadside(point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float, dwg: svgwrite.Drawing):
    group_msi_row = svgwrite.container.Group()
    hecto_offset = 0 if not point_info.pos_eigs.hectoletter else LANE_WIDTH * 25
    displacement = 0

    for nr in point_info.obj_eigs["Rijstrooknummers"]:
        msi_name = make_name(point_info, nr)
        displacement = info_offset + VISUAL_PLAY + (nr - 1) * (VISUAL_PLAY + MSIBOX_SIZE) + hecto_offset
        box_pos = (coords[0] + displacement, coords[1] - MSIBOX_SIZE / 2)
        square = dwg.rect(insert=box_pos,
                          size=(MSIBOX_SIZE, MSIBOX_SIZE),
                          fill="#1e1b17", stroke="black", stroke_width=STROKE,
                          onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                          onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
        group_msi_row.add(square)
        element_by_id[msi_name] = square, rotate_angle, coords

        # Extra elements
        box_center = (coords[0] + displacement + MSIBOX_SIZE / 2, coords[1])
        draw_all_legends(group_msi_row, msi_name, box_pos, box_center, MSIBOX_SIZE, dwg)

    group_text = svgwrite.container.Group()
    text_coords = (coords[0] + displacement + MSIBOX_SIZE * 1.3, coords[1])
    anchorpoint = "start" if -90 < rotate_angle < 90 else "end"
    text = svgwrite.text.Text(make_text_hecto(point_info.pos_eigs.km, point_info.pos_eigs.hectoletter),
                              insert=text_coords,
                              fill="white", font_family="Arial", dominant_baseline="central",
                              text_anchor=anchorpoint, font_size=TEXT_SIZE)
    group_text.add(text)
    group_text.rotate(-rotate_angle, center=text_coords)

    group_msi_row.add(group_text)
    group_msi_row.rotate(rotate_angle, center=coords)
    dwg.add(group_msi_row)


def display_MSI_onroad(point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float, dwg: svgwrite.Drawing):
    group_msi_row = svgwrite.container.Group()
    play = (LANE_WIDTH - MSIBOX_SIZE)/2
    displacement = 0

    for nr in point_info.obj_eigs["Rijstrooknummers"]:
        msi_name = make_name(point_info, nr)
        displacement = LANE_WIDTH * (nr - 1) - point_info.verw_eigs.aantal_hoofdstroken * LANE_WIDTH / 2
        box_pos = (coords[0] + displacement + play, coords[1] - MSIBOX_SIZE / 2)
        stroke = 0.3
        square = dwg.rect(insert=box_pos,
                          size=(MSIBOX_SIZE, MSIBOX_SIZE),
                          fill="#1e1b17", stroke="black", stroke_width=stroke,
                          onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                          onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
        group_msi_row.add(square)
        element_by_id[msi_name] = square, rotate_angle, coords

        # Extra elements
        box_center = (coords[0] + displacement + play + MSIBOX_SIZE / 2, coords[1])
        draw_all_legends(group_msi_row, msi_name, box_pos, box_center, MSIBOX_SIZE, dwg)

    group_text = svgwrite.container.Group()
    text_coords = (coords[0] + 2 + displacement + MSIBOX_SIZE, coords[1])
    anchorpoint = "start" if -90 < rotate_angle < 90 else "end"
    text = svgwrite.text.Text(make_text_hecto(point_info.pos_eigs.km, point_info.pos_eigs.hectoletter),
                              insert=text_coords,
                              fill="white", font_family="Arial", dominant_baseline="central",
                              text_anchor=anchorpoint, font_size=max(4.0, MSIBOX_SIZE*0.8))
    group_text.add(text)
    group_text.rotate(-rotate_angle, center=text_coords)

    group_msi_row.add(group_text)
    group_msi_row.rotate(rotate_angle, center=coords)
    dwg.add(group_msi_row)


def draw_all_legends(group_msi_row: svgwrite.container.Group, msi_name: str,
                     box_coords: tuple, center_coords: tuple, box_size: float, dwg: svgwrite.Drawing):
    box_west = box_coords[0]
    box_north = box_coords[1]
    box_east = box_west + box_size
    box_south = box_north + box_size
    clearance = box_size*0.2

    group_50 = group_msi_row.add(dwg.g(id=f"e[{msi_name}]", visibility="hidden"))
    group_50.add(svgwrite.text.Text(
        "50", insert=center_coords, fill="white", font_family="Courier New", font_size=box_size*0.60,
        text_anchor="middle", dominant_baseline="central"))

    group_70 = group_msi_row.add(dwg.g(id=f"g[{msi_name}]", visibility="hidden"))
    group_70.add(svgwrite.text.Text(
        "70", insert=center_coords, fill="white", font_family="Courier New", font_size=box_size*0.60,
        text_anchor="middle", dominant_baseline="central"))

    group_80 = group_msi_row.add(dwg.g(id=f"h[{msi_name}]", visibility="hidden"))
    group_80.add(svgwrite.text.Text(
        "80", insert=center_coords, fill="white", font_family="Courier New", font_size=box_size*0.60,
        text_anchor="middle", dominant_baseline="central"))

    group_90 = group_msi_row.add(dwg.g(id=f"i[{msi_name}]", visibility="hidden"))
    group_90.add(svgwrite.text.Text(
        "90", insert=center_coords, fill="white", font_family="Courier New", font_size=box_size*0.60,
        text_anchor="middle", dominant_baseline="central"))

    group_100 = group_msi_row.add(dwg.g(id=f"j[{msi_name}]", visibility="hidden"))
    group_100.add(svgwrite.text.Text(
        "100", insert=center_coords, fill="white", font_family="Courier New", font_size=box_size*0.60,
        text_anchor="middle", dominant_baseline="central"))

    group_overruling_blank = group_msi_row.add(dwg.g(id=f"o[{msi_name}]", visibility="hidden"))
    group_overruling_blank.add(dwg.rect(insert=box_coords,
                                        size=(MSIBOX_SIZE, MSIBOX_SIZE),
                                        fill="#1e1b17", stroke="none"))

    group_red_cross = group_msi_row.add(dwg.g(id=f"x[{msi_name}]", visibility="hidden"))
    group_red_cross.add(dwg.line(
        start=(box_west + clearance, box_north + clearance),
        end=(box_east - clearance, box_south - clearance),
        stroke="#FF0000", stroke_width=STROKE))  # \
    group_red_cross.add(dwg.line(
        start=(box_east - clearance, box_north + clearance),
        end=(box_west + clearance, box_south - clearance),
        stroke="#FF0000", stroke_width=STROKE))  # /

    group_green_arrow = group_msi_row.add(dwg.g(id=f"y[{msi_name}]", visibility="hidden"))
    group_green_arrow.add(dwg.line(
        start=(box_west + box_size / 2, box_north + clearance / 2),
        end=(box_west + box_size / 2, box_south - clearance * 1.5),
        stroke="#00FF00", stroke_width=STROKE))  # |
    group_green_arrow.add(dwg.line(
        start=(box_west + box_size / 2 + math.sqrt(STROKE / 2) / 2, box_south - clearance / 2),
        end=(box_west + clearance + math.sqrt(STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
        stroke="#00FF00", stroke_width=STROKE))  # \
    group_green_arrow.add(dwg.line(
        start=(box_west + box_size / 2 - math.sqrt(STROKE / 2) / 2, box_south - clearance / 2),
        end=(box_east - clearance - math.sqrt(STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
        stroke="#00FF00", stroke_width=STROKE))  # /

    group_left_arrow = group_msi_row.add(dwg.g(id=f"l[{msi_name}]", visibility="hidden"))
    group_left_arrow.add(dwg.line(
        start=(box_west + clearance - STROKE / 2, box_south - clearance),
        end=(box_east - clearance * 1.75, box_south - clearance),
        stroke="#FFFFFF", stroke_width=STROKE))  # _
    group_left_arrow.add(dwg.line(
        start=(box_west + clearance, box_south - clearance + STROKE / 2),
        end=(box_west + clearance, box_north + clearance * 1.75),
        stroke="#FFFFFF", stroke_width=STROKE))  # |
    group_left_arrow.add(dwg.line(
        start=(box_east - clearance, box_north + clearance),
        end=(box_west + clearance * 1.5, box_south - clearance * 1.5),
        stroke="#FFFFFF", stroke_width=STROKE))  # /

    group_right_arrow = group_msi_row.add(dwg.g(id=f"r[{msi_name}]", visibility="hidden"))
    group_right_arrow.add(dwg.line(
        start=(box_east - clearance + STROKE / 2, box_south - clearance),
        end=(box_west + clearance * 1.75, box_south - clearance),
        stroke="#FFFFFF", stroke_width=STROKE))  # _
    group_right_arrow.add(dwg.line(
        start=(box_east - clearance, box_south - clearance + STROKE / 2),
        end=(box_east - clearance, box_north + clearance * 1.75),
        stroke="#FFFFFF", stroke_width=STROKE))  # |
    group_right_arrow.add(dwg.line(
        start=(box_west + clearance, box_north + clearance),
        end=(box_east - clearance * 1.5, box_south - clearance * 1.5),
        stroke="#FFFFFF", stroke_width=STROKE))  # \

    group_eor = group_msi_row.add(dwg.g(id=f"z[{msi_name}]", visibility="hidden"))
    group_eor.add(dwg.circle(
        center=center_coords,
        r=box_size * 0.45,
        fill="none", stroke="#FFFFFF", stroke_width=STROKE))
    group_eor.add(dwg.line(
        start=(box_east - clearance - STROKE * 1.5, box_north + clearance - STROKE * 1.5),
        end=(box_west + clearance - STROKE * 1.5, box_south - clearance - STROKE * 1.5),
        stroke="#FFFFFF", stroke_width=STROKE))
    group_eor.add(dwg.line(
        start=(box_east - clearance, box_north + clearance),
        end=(box_west + clearance, box_south - clearance),
        stroke="#FFFFFF", stroke_width=STROKE))
    group_eor.add(dwg.line(
        start=(box_east - clearance + STROKE * 1.5, box_north + clearance + STROKE * 1.5),
        end=(box_west + clearance + STROKE * 1.5, box_south - clearance + STROKE * 1.5),
        stroke="#FFFFFF", stroke_width=STROKE))

    group_flashers = group_msi_row.add(dwg.g(id=f"a[{msi_name}]", visibility="hidden"))
    group_flashers.add(dwg.circle(
        center=(box_west + clearance / 2, box_north + clearance / 2),
        r=clearance / 4, fill="yellow"))  # top-left
    group_flashers.add(dwg.circle(
        center=(box_east - clearance / 2, box_north + clearance / 2),
        r=clearance / 4, fill="yellow"))  # top-right
    group_flashers.add(dwg.circle(
        center=(box_west + clearance / 2, box_south - clearance / 2),
        r=clearance / 4, fill="black"))  # bottom-left
    group_flashers.add(dwg.circle(
        center=(box_east - clearance / 2, box_south - clearance / 2),
        r=clearance / 4, fill="black"))  # bottom-right

    for circle in group_flashers.elements[:2]:
        circle.add(dwg.animate("fill", attributeType="XML", from_="yellow", to="black",
                               id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))
    for circle in group_flashers.elements[-2:]:
        circle.add(dwg.animate("fill", attributeType="XML", from_="black", to="yellow",
                               id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))

    group_red_ring = group_msi_row.add(dwg.g(id=f"b[{msi_name}]", visibility="hidden"))
    group_red_ring.add(dwg.circle(
        center=center_coords,
        r=box_size * 0.40,
        fill="none", stroke="#FF0000", stroke_width=STROKE))


def display_vergence(point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float,
                     dwg: svgwrite.Drawing):
    group_vergence = svgwrite.container.Group()

    text = svgwrite.text.Text(f"{point_info.pos_eigs.km} {point_info.obj_eigs['Type']}",
                              insert=(coords[0] + 1 + info_offset, coords[1]),
                              fill="white", font_family="Arial", dominant_baseline="central", font_size=4)

    group_vergence.add(text)
    group_vergence.rotate(rotate_angle, center=coords)
    dwg.add(group_vergence)


def draw_msi_relations(dwg: svgwrite.Drawing):
    # Draw primary relations
    for element_id in element_by_id.keys():
        start_element, start_rotation, start_origin = element_by_id[element_id]
        start_pos = get_center_coords(start_element, start_rotation, start_origin)
        for row in netwerk.MSIrows:
            for msi in row.MSIs.values():
                if msi.name == element_id:
                    if msi.properties["d"]:
                        end_element, end_rotation, end_origin = element_by_id[msi.properties["d"]]
                        end_pos = get_center_coords(end_element, end_rotation, end_origin)
                        draw_msi_relation("p", start_pos, end_pos, dwg)
                    if msi.properties["ds"]:
                        for end_id in msi.properties["ds"]:
                            end_element, end_rotation, end_origin = element_by_id[end_id]
                            end_pos = get_center_coords(end_element, end_rotation, end_origin)
                            draw_msi_relation("s", start_pos, end_pos, dwg)
                    if msi.properties["dt"]:
                        end_element, end_rotation, end_origin = element_by_id[msi.properties["dt"]]
                        end_pos = get_center_coords(end_element, end_rotation, end_origin)
                        draw_msi_relation("t", start_pos, end_pos, dwg)
                    if msi.properties["db"]:
                        end_element, end_rotation, end_origin = element_by_id[msi.properties["db"]]
                        end_pos = get_center_coords(end_element, end_rotation, end_origin)
                        draw_msi_relation("b", start_pos, end_pos, dwg)
                    if msi.properties["dn"]:
                        end_element, end_rotation, end_origin = element_by_id[msi.properties["dn"]]
                        end_pos = get_center_coords(end_element, end_rotation, end_origin)
                        draw_msi_relation("n", start_pos, end_pos, dwg)


def draw_msi_relation(rel_type: str, start_pos: tuple, end_pos: tuple, dwg: svgwrite.Drawing):
    dwg.add(dwg.line(start=start_pos, end=end_pos, stroke=COLORMAP[rel_type], stroke_width=STROKE*2))
    dwg.add(dwg.circle(center=start_pos, r=STROKE*4, fill=COLORMAP[rel_type]))
    dwg.add(dwg.circle(center=end_pos, r=STROKE*4, fill=COLORMAP[rel_type]))


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


def make_name(point_info, nr) -> str:
    if point_info.pos_eigs.hectoletter:
        return f"{point_info.pos_eigs.wegnummer}_{point_info.pos_eigs.hectoletter.upper()}:{point_info.pos_eigs.km}:{nr}"
    else:
        return f"{point_info.pos_eigs.wegnummer}{point_info.pos_eigs.rijrichting}:{point_info.pos_eigs.km}:{nr}"


def make_text_hecto(km: float, letter: str | None) -> str:
    if letter:
        return f"{km} {letter}"
    return f"{km}"


# Create SVG drawing
dwg = svgwrite.Drawing(filename="Server/Data/WEGGEG/road_visualization.svg", size=(1000, 1000 * RATIO), profile="full")

# Background
dwg.add(dwg.rect(insert=(TOP_LEFT_X, TOP_LEFT_Y), size=(VIEWBOX_WIDTH, VIEWBOX_HEIGHT), fill="green"))

# Section data (roads)
print("Sectiedata visualiseren...")
for section_id, section_info in wegmodel.sections.items():
    svg_add_section(section_id, section_info, dwg)

# Point data (MSIs, convergence, divergence)
print("Puntdata visualiseren...")
points = wegmodel.get_points_info()  # Specify "MSI" here when *vergence points no longer desired to visualise.
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
