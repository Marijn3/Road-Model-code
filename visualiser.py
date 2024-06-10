from road_model import WegModel, ObjectInfo, PositieEigenschappen
from msi_relations import MSINetwerk, MSIRow
import svgwrite
import os
from shapely import *
from utils import *

logger = logging.getLogger(__name__)


class SvgMaker:
    
    __C_TRANSPARENT = "#6D876D"
    __C_HIGHLIGHT = "#D06E7C"
    __C_NARROWING = "#736D55"
    __C_TAPER = "#73677C"
    __C_ASPHALT = "grey"
    __C_WHITE = "#faf8f5"

    __CARRIAGEWAY_COLORMAP = {
        1: "#256BE4",
        2: "#BA7A03",
        3: "#7B0970",
        4: "#B2C200",
    }

    __RELATION_COLORMAP = {
        "d": "cyan", "u": "cyan",  # Primary
        "s": "magenta",  # Secondary
        "t": "red",  # Taper
        "b": "orange",  # Broadening
        "n": "yellow",  # Narrowing
    }
    
    def __init__(self, wegmodel: WegModel, msis: MSINetwerk, naam_relatiebestand: str,
                 output_folder: str, formaat: int = 1000, msis_boven_weg_tekenen: bool = False):
        self.__wegmodel = wegmodel
        self.__msi_network = msis
        self.__relation_file = naam_relatiebestand
        self.__outfile = f"{output_folder}/RoadModelVisualisation.svg"
        self.__size = formaat
        self.__msis_on_road = msis_boven_weg_tekenen
        self.__element_by_id = {}

        # Generate road model output folder if it does not exist.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Visualiser parameters (constants)
        self.__LANE_WIDTH = 3.5

        if msis_boven_weg_tekenen:
            self.__MSIBOX_SIZE = self.__LANE_WIDTH * 0.8
            self.__TEXT_SIZE = max(4.0, self.__MSIBOX_SIZE * 0.8)
            self.__VISUAL_PLAY = self.__MSIBOX_SIZE * 0.2
            self.__BASE_STROKE = self.__MSIBOX_SIZE * 0.07
        else:
            self.__MSIBOX_SIZE = 20
            self.__TEXT_SIZE = self.__MSIBOX_SIZE * 0.6
            self.__VISUAL_PLAY = self.__MSIBOX_SIZE * 0.2
            self.__BASE_STROKE = self.__MSIBOX_SIZE * 0.05

        # Visualisation extent
        bottom_right, _, top_left, _, _ = get_coordinates(self.__wegmodel.extent)
        self.__west, self.__north = top_left
        self.__east, self.__south = bottom_right
        self.__viewbox_width = abs(self.__west - self.__east)
        self.__viewbox_height = abs(self.__north - self.__south)
        self.__ratio = self.__viewbox_height / self.__viewbox_width

        # Create instances for visualisation
        self.__dwg = svgwrite.Drawing(filename=self.__outfile,
                                      size=(self.__size, self.__size * self.__ratio),
                                      profile="full",
                                      id="svg5")  # This specific ID tag is used by JvM script

        # Determine 'layer' order
        self.__g_background = self.__dwg.add(self.__dwg.g(id="background"))
        self.__g_road = self.__dwg.add(self.__dwg.g(id="road"))
        self.__g_msi_relations = self.__dwg.add(self.__dwg.g(id="nametags_MSI"))  # Tag for visibility toggle in UI
        self.__g_points = self.__dwg.add(self.__dwg.g(id="points"))

        # Visualise the image part by part
        self.__visualise_background()
        self.__visualise_roads()
        self.__visualise_msis()
        self.__save_image()

    def __visualise_background(self):
        # Background
        self.__g_background.add(
            self.__dwg.rect(insert=(self.__west, self.__north),
                            size=(self.__viewbox_width, self.__viewbox_height), fill="green"))

    def __visualise_roads(self):
        logger.info("Sectiedata visualiseren...")
        for section_id, section_info in self.__wegmodel.sections.items():
            self.__svg_draw_section(section_id, section_info)

    def __visualise_msis(self):
        logger.info("MSI-posities visualiseren...")
        for msi_row in self.__msi_network.MSIrows:
            self.__svg_draw_msi_position(msi_row)

        logger.info("MSI-relaties visualiseren...")
        self.__svg_draw_msi_relations()

    def __save_image(self):
        self.__dwg.viewbox(minx=self.__west, miny=self.__north, width=self.__viewbox_width,
                           height=self.__viewbox_height)
        self.__dwg.save(pretty=True, indent=2)
        logger.info("Visualisatie succesvol afgerond.")

    def __get_road_color(self, section_info: ObjectInfo) -> str:
        """
        Determines color for road section visualisation based on the provided road properties.
        Args:
            section_info (ObjectInfo): Properties of road section.
        Returns:
            Color name as string.
        """
        if self.__wegmodel.find_gap([lane for lane in section_info.obj_eigs.keys() if isinstance(lane, int)]):
            return self.__C_TRANSPARENT
        elif "Special" in section_info.obj_eigs.keys():
            if "Taper" in section_info.obj_eigs["Special"][0]:
                return self.__C_TAPER
            else:
                return self.__C_NARROWING
        elif section_info.verw_eigs.heeft_verwerkingsfout:
            return self.__C_HIGHLIGHT
        else:
            return self.__C_ASPHALT

    def __get_flipped_coords(self, geom: LineString | Point) -> list[tuple]:
        """
        Flips geometries around the top border of the frame and returns the coordinates.
        This is necessary for visualisation, as the RD-coordinate system and the SVG
        coordinate system have a different definition of their y-axis.
        Args:
            geom (LineString or Point): Geometry to be flipped.
        Returns:
            List of coordinates making up the flipped geometry.
        """
        return [(coord[0], self.__north - (coord[1] - self.__north)) for coord in geom.coords]

    def __get_offset_coords(self, section_info: ObjectInfo, geom: LineString,
                            offset: float = 0, lane_nr: int = None) -> list[tuple]:
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
        geom = self.__adjust_line_ends(section_info, geom, lane_nr)
        if offset == 0:
            return self.__get_flipped_coords(geom)
        else:
            offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
            return self.__get_flipped_coords(offset_geom)

    def __adjust_line_ends(self, section_info: ObjectInfo, geom: LineString, lane_nr: int) -> LineString:
        if not lane_nr or (lane_nr not in section_info.verw_eigs.start_kenmerk
                           and lane_nr not in section_info.verw_eigs.einde_kenmerk):
            return geom

        if (lane_nr in section_info.verw_eigs.start_kenmerk
                and section_info.verw_eigs.start_kenmerk[lane_nr] == "Uitrijstrook"):
            # Move first point
            change_start = True
            point_to_displace = geom.coords[0]
            if get_num_coordinates(geom) < 3:
                delta_x = geom.coords[1][0] - geom.coords[0][0]
                delta_y = geom.coords[1][1] - geom.coords[0][1]
            elif get_num_coordinates(geom) < 4:
                delta_x = geom.coords[2][0] - geom.coords[0][0]
                delta_y = geom.coords[2][1] - geom.coords[0][1]
            else:
                delta_x = geom.coords[3][0] - geom.coords[0][0]
                delta_y = geom.coords[3][1] - geom.coords[0][1]
        elif (lane_nr in section_info.verw_eigs.einde_kenmerk and
                section_info.verw_eigs.einde_kenmerk[lane_nr] == "Invoegstrook"):
            # Move last point
            change_start = False
            point_to_displace = geom.coords[-1]
            if get_num_coordinates(geom) < 3:
                delta_x = geom.coords[-1][0] - geom.coords[-2][0]
                delta_y = geom.coords[-1][1] - geom.coords[-2][1]
            elif get_num_coordinates(geom) < 4:
                delta_x = geom.coords[-1][0] - geom.coords[-3][0]
                delta_y = geom.coords[-1][1] - geom.coords[-3][1]
            else:
                delta_x = geom.coords[-1][0] - geom.coords[-4][0]
                delta_y = geom.coords[-1][1] - geom.coords[-4][1]
        else:
            return geom

        angle_rad = math.atan2(delta_y, delta_x)
        tangent_vector = [-math.sin(angle_rad), math.cos(angle_rad)]

        displacement = self.__LANE_WIDTH

        displaced_point = Point(point_to_displace[0] + tangent_vector[0] * displacement,
                                point_to_displace[1] + tangent_vector[1] * displacement)

        if get_num_coordinates(geom) < 3:
            if change_start:
                return LineString([displaced_point.coords[0]] + [coord for coord in geom.coords[1:]])
            else:
                return LineString([coord for coord in geom.coords[:-1]] + [displaced_point.coords[0]])

        # For section geometries with at least three points, the second (to last) point is removed.
        # This improves the geometry visualisation.
        if change_start:
            return LineString([displaced_point.coords[0]] + [coord for coord in geom.coords[2:]])
        else:
            return LineString([coord for coord in geom.coords[:-2]] + [displaced_point.coords[0]])

    def __check_points_on_line(self, sid: int) -> list[ObjectInfo]:
        """
        Finds any *vergence points on the section.
        Args:
            sid (int): Section ID to search for.
        Returns:
            ObjectInfo of all *vergence points on the section in a list
        """
        points_info = []
        for point_info in self.__wegmodel.get_points_info("*vergentie"):
            if sid in point_info.verw_eigs.sectie_ids:
                points_info.append(point_info)
        return points_info

    def __get_changed_geometry(self, section_id: int, section_info: ObjectInfo,
                               points_info: list[ObjectInfo]) -> LineString:
        """
        Get the geometry of the section, where one of the endpoints is displaced if it overlaps with a
        *vergentiepunt point, and it is necessary to move it. Also adds a general property to the section
        that details whether there is a *vergence point at the start or end of it.
        Args:
            section_id (int): ID of section to be moved.
            section_info (ObjectInfo): All data of the section to be moved.
            points_info (list[ObjectINfo]): Data of the points on the section where the geometry should be moved.
        Returns:
            The geometry of the section, where one of the endpoints is displaced if necessary.
        """
        line_geom = section_info.pos_eigs.geometrie

        for point_info in points_info:
            # Case by case analysis of what should be done to the line geometry.
            point_type = point_info.obj_eigs["Type"]

            point_is_at_line_start = dwithin(Point(line_geom.coords[0]),
                                             point_info.pos_eigs.geometrie,
                                             DISTANCE_TOLERANCE)
            point_is_at_line_end = dwithin(Point(line_geom.coords[-1]),
                                           point_info.pos_eigs.geometrie,
                                           DISTANCE_TOLERANCE)

            if point_type == "Splitsing" and point_is_at_line_start:
                other_lane_id = list(set(point_info.verw_eigs.uitgaande_secties) - {section_id})[0]
                line_geom = self.__move_endpoint(section_info, line_geom, other_lane_id, point_info, True)
            elif point_type == "Samenvoeging" and point_is_at_line_end:
                other_lane_id = list(set(point_info.verw_eigs.ingaande_secties) - {section_id})[0]
                line_geom = self.__move_endpoint(section_info, line_geom, other_lane_id, point_info, False)
            elif point_type == "Uitvoeging" and point_is_at_line_start:
                other_lane_id = list(set(point_info.verw_eigs.uitgaande_secties) - {section_id})[0]
                line_geom = self.__move_endpoint(section_info, line_geom, other_lane_id, point_info, True)
            elif point_type == "Invoeging" and point_is_at_line_end:
                other_lane_id = list(set(point_info.verw_eigs.ingaande_secties) - {section_id})[0]
                line_geom = self.__move_endpoint(section_info, line_geom, other_lane_id, point_info, False)
            else:
                # This is for all cases where a section DOES connect to a *vergence point, but should not be moved.
                continue

        return line_geom

    def __move_endpoint(self, this_section_info: ObjectInfo, line_geom: LineString, other_section_id: int,
                        point_info: ObjectInfo, change_start: bool = True):
        other_section_info = self.__wegmodel.sections[other_section_id]

        angle_radians = math.radians(point_info.verw_eigs.lokale_hoek)
        tangent_vector = [-math.sin(angle_radians), math.cos(angle_radians)]  # Rotated by 90 degrees

        this_section_max_lane_nr = max([key for key in this_section_info.obj_eigs.keys() if isinstance(key, int)])
        other_section_max_lane_nr = max([key for key in other_section_info.obj_eigs.keys() if isinstance(key, int)])

        this_is_continuous = (this_section_info.obj_eigs[this_section_max_lane_nr] == "Puntstuk"
                              or other_section_info.obj_eigs[1] == "Puntstuk")
        other_is_continuous = (other_section_info.obj_eigs[other_section_max_lane_nr] == "Puntstuk"
                               or this_section_info.obj_eigs[1] == "Puntstuk")

        assert not (this_is_continuous and other_is_continuous),\
            f"Twee secties met puntstuk bij {point_info.pos_eigs}\n{this_section_info}\n{other_section_info}"
        assert (this_is_continuous or other_is_continuous),\
            f"Geen sectie met puntstuk bij {point_info.pos_eigs}\n{this_section_info}\n{other_section_info}"

        displacement = 0
        n_lanes_largest = point_info.verw_eigs.aantal_hoofdstroken

        if this_is_continuous:
            n_lanes_a = this_section_info.verw_eigs.aantal_hoofdstroken
            displacement = self.__LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)

        elif other_is_continuous:
            n_lanes_a = other_section_info.verw_eigs.aantal_hoofdstroken
            n_lanes_b = this_section_info.verw_eigs.aantal_hoofdstroken
            displacement = (self.__LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)
                            - self.__LANE_WIDTH / 2 * (n_lanes_a + n_lanes_b))

        if change_start:
            point_to_displace = line_geom.coords[0]
        else:
            point_to_displace = line_geom.coords[-1]

        displaced_point = Point(point_to_displace[0] + tangent_vector[0] * displacement,
                                point_to_displace[1] + tangent_vector[1] * displacement)

        if get_num_coordinates(line_geom) < 3:
            if change_start:
                return LineString([displaced_point.coords[0]] + [coord for coord in line_geom.coords[1:]])
            else:
                return LineString([coord for coord in line_geom.coords[:-1]] + [displaced_point.coords[0]])

        # For section geometries with at least three points, the second (to last) point is removed.
        # This improves the geometry visualisation.
        if change_start:
            return LineString([displaced_point.coords[0]] + [coord for coord in line_geom.coords[2:]])
        else:
            return LineString([coord for coord in line_geom.coords[:-2]] + [displaced_point.coords[0]])

    def __svg_draw_section(self, section_id: int, section_info: ObjectInfo):
        points_on_line = self.__check_points_on_line(section_id)

        if points_on_line:
            adjusted_geom = self.__get_changed_geometry(section_id, section_info, points_on_line)
        else:
            adjusted_geom = section_info.pos_eigs.geometrie

        n_main_lanes, n_total_lanes = self.__wegmodel.get_n_lanes(section_info.obj_eigs)

        n_main_lanes = section_info.verw_eigs.aantal_hoofdstroken
        n_lanes_left = section_info.verw_eigs.aantal_rijstroken_links
        n_lanes_right = section_info.verw_eigs.aantal_rijstroken_rechts

        if n_main_lanes < 1 or n_total_lanes < 1:
            # These sections are not added. This is fine, because they fall outside the visualisation frame.
            return

        # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
        offset = self.__LANE_WIDTH * (n_lanes_left - n_lanes_right) / 2

        asphalt_coords = self.__get_offset_coords(section_info, adjusted_geom, offset)
        color = self.__get_road_color(section_info)
        width = self.__LANE_WIDTH * n_total_lanes

        self.__g_road.add(self.__dwg.polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width))

        should_have_marking = color not in [self.__C_TRANSPARENT]

        if should_have_marking:
            self.__determine_lane_marking(section_info, adjusted_geom)

    def __determine_lane_marking(self, section_info: ObjectInfo,geom: LineString):
        lane_numbers = sorted([nr for nr, lane in section_info.obj_eigs.items() if isinstance(nr, int)])

        # Offset centered around main lanes. Positive offset distance is on the left side of the LineString.
        marking_offsets = [(self.__LANE_WIDTH * section_info.verw_eigs.aantal_hoofdstroken) / 2
                           + self.__LANE_WIDTH * section_info.verw_eigs.aantal_rijstroken_links
                           - self.__LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

        # TODO: Replace with approach using lane marking table.

        first_lane_nr = lane_numbers[0]
        last_lane_nr = lane_numbers[-1]
        next_lane = None

        # Exclude puntstuk from counting as the last lane
        if section_info.obj_eigs[last_lane_nr] == "Puntstuk":
            last_lane_nr = lane_numbers[-2]

        # Add first solid marking (leftmost), except when the first lane is a vluchtstrook.
        line_coords = self.__get_offset_coords(section_info, geom, marking_offsets.pop(0))
        if section_info.obj_eigs[first_lane_nr] not in ["Vluchtstrook"]:
            self.__draw_markerline(line_coords)
        # Also add puntstuk if it is the very first registration
        if section_info.obj_eigs[first_lane_nr] == "Puntstuk":
            if section_info.verw_eigs.vergentiepunt_start:
                self.__draw_markerline(line_coords, "Punt-start", direction=-1)
            elif section_info.verw_eigs.vergentiepunt_einde:
                self.__draw_markerline(line_coords, "Punt-einde", direction=-1)

        # Add middle markings. All of these markings have a this_lane and a next_lane
        for this_lane_number in lane_numbers[:-1]:
            next_lane_number = this_lane_number + 1

            this_lane = section_info.obj_eigs[this_lane_number]
            next_lane = section_info.obj_eigs[next_lane_number]

            # Puntstuk has already been drawn
            if this_lane == "Puntstuk":
                continue

            # A puntstuk that is not the first lane, is the final lane.
            if next_lane == "Puntstuk":
                line_coords = self.__get_offset_coords(section_info, geom, marking_offsets.pop(0), this_lane_number)
                self.__draw_markerline(line_coords)
                if section_info.verw_eigs.vergentiepunt_start:
                    self.__draw_markerline(line_coords, "Punt-start", direction=1)
                elif section_info.verw_eigs.vergentiepunt_einde:
                    self.__draw_markerline(line_coords, "Punt-einde", direction=1)
                break

            # Puntstuk cases have been handled, now the normal cases.
            line_coords = self.__get_offset_coords(section_info, geom, marking_offsets.pop(0), this_lane_number)

            # An emergency lane is demarcated with a solid line.
            if this_lane == "Vluchtstrook" or next_lane == "Vluchtstrook":
                self.__draw_markerline(line_coords)

            # A plus lane is demarcated with a 9-3 dashed line.
            elif this_lane == "Plusstrook":
                self.__draw_markerline(line_coords, "Streep-9-3")

            # If the next lane is a samenvoeging, use normal dashed lane marking. TODO: Why??
            # elif next_lane == "Samenvoeging":
            #     self.__draw_markerline(line_coords, "Streep-3-9")

            # A rush hour lane (on the final lane) has special lines.
            elif next_lane == "Spitsstrook" and next_lane_number == last_lane_nr:
                self.__draw_markerline(line_coords)

            # All other lanes are separated by dashed lines.
            elif this_lane == next_lane:
                self.__draw_markerline(line_coords, "Streep-3-9")

            # If the lane types are not the same, block markings are used.
            else:
                self.__draw_markerline(line_coords, "Blok")

        # Add last solid marking (rightmost), except when the last lane is a vluchtstrook or puntstuk.
        # Spitsstrook has special lane marking.
        line_coords = self.__get_offset_coords(section_info, geom, marking_offsets.pop(0), last_lane_nr)
        if next_lane == "Spitsstrook":
            self.__draw_markerline(line_coords, "Dun")
        elif next_lane not in ["Vluchtstrook", "Puntstuk"]:
            self.__draw_markerline(line_coords)

    def __draw_markerline(self, coords: list[tuple], linetype: str = "full", direction: int = 1):
        if linetype == "Streep-3-9":
            self.__draw_line(coords, 0.4, "3 9")
        elif linetype == "Streep-9-3":
            self.__draw_line(coords, 0.4, "9 3")
        elif linetype == "Blok":
            self.__draw_line(coords, 0.6, "0.8 4")
        elif linetype == "Punt-start" or linetype == "Punt-einde":
            self.__draw_triangle(coords, linetype, direction)
            self.__draw_line(coords, 0.4)
        elif linetype == "Dun":
            self.__draw_line(coords, 0.2)
        else:
            self.__draw_line(coords, 0.4)

    def __draw_line(self, coords: list[tuple], width: float, dasharray: str = ""):
        if dasharray:
            line = self.__dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width,
                                       stroke_dasharray=dasharray)
        else:
            line = self.__dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width)
        self.__g_road.add(line)

    def __draw_triangle(self, coords: list[tuple], linetype: str, direction: int = 1):
        triangle_end = coords[-1] if linetype == "Punt-start" else coords[0]

        vec = [coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]]
        mag = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        third_point = (triangle_end[0] + self.__LANE_WIDTH * direction * -vec[1] / mag,
                       triangle_end[1] + self.__LANE_WIDTH * direction * vec[0] / mag)
        all_points = coords + [third_point]

        triangle = self.__dwg.polygon(points=all_points, fill=self.__C_WHITE)
        self.__g_road.add(triangle)

    def __svg_draw_msi_position(self, msi_row: MSIRow):
        point_info = msi_row.info
        coords = self.__get_flipped_coords(point_info.pos_eigs.geometrie)[0]
        # TODO: Update these calculations so they are uniform with the others (lanes left and right of...)
        info_offset = self.__LANE_WIDTH * (point_info.verw_eigs.aantal_stroken + point_info.verw_eigs.aantal_stroken -
                                           point_info.verw_eigs.aantal_hoofdstroken) / 2
        rotate_angle = 90 - point_info.verw_eigs.lokale_hoek

        if point_info.obj_eigs["Type"] == "Signalering":
            if self.__msis_on_road:
                self.__display_MSI_onroad(msi_row, coords, rotate_angle)
            else:
                self.__display_MSI_roadside(msi_row, coords, info_offset, rotate_angle)
        else:
            self.__display_vergence(point_info, coords, info_offset, rotate_angle)

    def __display_MSI_roadside(self, msi_row: MSIRow, coords: tuple, info_offset: float, rotate_angle: float):
        g_msi_row = self.__g_points.add(self.__dwg.g())
        hecto_offset = 0 if msi_row.info.pos_eigs.hectoletter in ["", "w"] else self.__LANE_WIDTH * 25
        displacement = 0

        for nr in msi_row.info.obj_eigs["Rijstrooknummers"]:
            msi_name = make_name(msi_row.info, nr)
            displacement = (info_offset + self.__VISUAL_PLAY + (nr - 1) *
                            (self.__VISUAL_PLAY + self.__MSIBOX_SIZE) + hecto_offset)
            box_pos = (coords[0] + displacement, coords[1] - self.__MSIBOX_SIZE / 2)
            square = self.__draw_msi(box_pos, msi_row.MSIs[nr].properties["CW_num"])
            g_msi_row.add(square)
            self.__element_by_id[msi_name] = square, rotate_angle, coords

            # Extra elements
            box_center = (coords[0] + displacement + self.__MSIBOX_SIZE / 2, coords[1])
            self.__draw_all_legends(g_msi_row, msi_name, box_pos, box_center, self.__MSIBOX_SIZE)

        text_coords = (coords[0] + displacement + self.__MSIBOX_SIZE * 1.3, coords[1])

        g_msi_text = self.__draw_msi_text(msi_row.info, text_coords, rotate_angle)
        g_msi_row.add(g_msi_text)
        g_msi_row.rotate(rotate_angle, center=coords)

    def __display_MSI_onroad(self, msi_row: MSIRow, coords: tuple, rotate_angle: float):
        g_msi_row = self.__g_points.add(self.__dwg.g())
        play = (self.__LANE_WIDTH - self.__MSIBOX_SIZE) / 2
        displacement = 0

        for nr in msi_row.info.obj_eigs["Rijstrooknummers"]:
            msi_name = make_name(msi_row.info, nr)
            displacement = self.__LANE_WIDTH * (nr - 1) - msi_row.info.verw_eigs.aantal_hoofdstroken * self.__LANE_WIDTH / 2
            box_pos = (coords[0] + displacement + play, coords[1] - self.__MSIBOX_SIZE / 2)
            square = self.__draw_msi(box_pos, msi_row.MSIs[nr].properties["CW_num"])
            g_msi_row.add(square)
            self.__element_by_id[msi_name] = square, rotate_angle, coords

            # Extra elements
            box_center = (coords[0] + displacement + play + self.__MSIBOX_SIZE / 2, coords[1])
            self.__draw_all_legends(g_msi_row, msi_name, box_pos, box_center, self.__MSIBOX_SIZE)

        text_coords = (coords[0] + 2 + displacement + self.__MSIBOX_SIZE, coords[1])
        
        g_msi_text = self.__draw_msi_text(msi_row.info, text_coords, rotate_angle)
        g_msi_row.add(g_msi_text)
        g_msi_row.rotate(rotate_angle, center=coords)

    def __draw_msi(self, box_pos, cw_number: int):
        stroke_color = self.__CARRIAGEWAY_COLORMAP.get(cw_number, "black")
        return self.__dwg.rect(insert=box_pos,
                               size=(self.__MSIBOX_SIZE, self.__MSIBOX_SIZE),
                               fill="#1e1b17", stroke=stroke_color, stroke_width=self.__BASE_STROKE,
                               onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                               onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
    
    def __draw_msi_text(self, point_info, text_coords, rotate_angle):
        g_text = self.__dwg.g()
        anchorpoint = "start" if -90 < rotate_angle < 90 else "end"
        text = self.__dwg.text(make_msi_text(point_info.pos_eigs),
                               insert=text_coords, text_anchor=anchorpoint, font_size=self.__TEXT_SIZE,
                               fill="white", font_family="Arial", dominant_baseline="central")
        g_text.add(text)
        g_text.rotate(-rotate_angle, center=text_coords)
        return g_text

    def __draw_all_legends(self, g_msi_row: svgwrite.container.Group, msi_name: str,
                           box_coords: tuple, center_coords: tuple, box_size: float):
        box_west = box_coords[0]
        box_north = box_coords[1]
        box_east = box_west + box_size
        box_south = box_north + box_size
        clearance = box_size*0.2
        text_center_coords = (center_coords[0], center_coords[1] + box_size*0.06)

        g_50 = g_msi_row.add(self.__dwg.g(id=f"e[{msi_name}]", visibility="hidden"))
        g_50.add(self.__dwg.text(
            "50", insert=text_center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_70 = g_msi_row.add(self.__dwg.g(id=f"g[{msi_name}]", visibility="hidden"))
        g_70.add(self.__dwg.text(
            "70", insert=text_center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_80 = g_msi_row.add(self.__dwg.g(id=f"h[{msi_name}]", visibility="hidden"))
        g_80.add(self.__dwg.text(
            "80", insert=text_center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_90 = g_msi_row.add(self.__dwg.g(id=f"i[{msi_name}]", visibility="hidden"))
        g_90.add(self.__dwg.text(
            "90", insert=text_center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_100 = g_msi_row.add(self.__dwg.g(id=f"j[{msi_name}]", visibility="hidden"))
        g_100.add(self.__dwg.text(
            "100", insert=text_center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            letter_spacing="-0.5", text_anchor="middle", dominant_baseline="middle"))

        g_overruling_blank = g_msi_row.add(self.__dwg.g(id=f"o[{msi_name}]", visibility="hidden"))
        g_overruling_blank.add(self.__dwg.rect(insert=box_coords,
                                               size=(self.__MSIBOX_SIZE, self.__MSIBOX_SIZE),
                                               fill="#1e1b17", stroke="none"))

        g_red_cross = g_msi_row.add(self.__dwg.g(id=f"x[{msi_name}]", visibility="hidden"))
        g_red_cross.add(self.__dwg.line(
            start=(box_west + clearance, box_north + clearance),
            end=(box_east - clearance, box_south - clearance),
            stroke="#FF0000", stroke_width=self.__BASE_STROKE))  # \
        g_red_cross.add(self.__dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance, box_south - clearance),
            stroke="#FF0000", stroke_width=self.__BASE_STROKE))  # /

        g_green_arrow = g_msi_row.add(self.__dwg.g(id=f"y[{msi_name}]", visibility="hidden"))
        g_green_arrow.add(self.__dwg.line(
            start=(box_west + box_size / 2, box_north + clearance / 2),
            end=(box_west + box_size / 2, box_south - clearance * 1.5),
            stroke="#00FF00", stroke_width=self.__BASE_STROKE))  # |
        g_green_arrow.add(self.__dwg.line(
            start=(box_west + box_size / 2 + math.sqrt(self.__BASE_STROKE / 2) / 2, box_south - clearance / 2),
            end=(box_west + clearance + math.sqrt(self.__BASE_STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
            stroke="#00FF00", stroke_width=self.__BASE_STROKE))  # \
        g_green_arrow.add(self.__dwg.line(
            start=(box_west + box_size / 2 - math.sqrt(self.__BASE_STROKE / 2) / 2, box_south - clearance / 2),
            end=(box_east - clearance - math.sqrt(self.__BASE_STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
            stroke="#00FF00", stroke_width=self.__BASE_STROKE))  # /

        g_left_arrow = g_msi_row.add(self.__dwg.g(id=f"l[{msi_name}]", visibility="hidden"))
        g_left_arrow.add(self.__dwg.line(
            start=(box_west + clearance - self.__BASE_STROKE / 2, box_south - clearance),
            end=(box_east - clearance * 1.75, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # _
        g_left_arrow.add(self.__dwg.line(
            start=(box_west + clearance, box_south - clearance + self.__BASE_STROKE / 2),
            end=(box_west + clearance, box_north + clearance * 1.75),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # |
        g_left_arrow.add(self.__dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance * 1.5, box_south - clearance * 1.5),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # /

        g_right_arrow = g_msi_row.add(self.__dwg.g(id=f"r[{msi_name}]", visibility="hidden"))
        g_right_arrow.add(self.__dwg.line(
            start=(box_east - clearance + self.__BASE_STROKE / 2, box_south - clearance),
            end=(box_west + clearance * 1.75, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # _
        g_right_arrow.add(self.__dwg.line(
            start=(box_east - clearance, box_south - clearance + self.__BASE_STROKE / 2),
            end=(box_east - clearance, box_north + clearance * 1.75),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # |
        g_right_arrow.add(self.__dwg.line(
            start=(box_west + clearance, box_north + clearance),
            end=(box_east - clearance * 1.5, box_south - clearance * 1.5),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))  # \

        g_eor = g_msi_row.add(self.__dwg.g(id=f"z[{msi_name}]", visibility="hidden"))
        g_eor.add(self.__dwg.circle(
            center=center_coords,
            r=box_size * 0.45,
            fill="none", stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))
        g_eor.add(self.__dwg.line(
            start=(box_east - clearance - self.__BASE_STROKE * 1.5, box_north + clearance - self.__BASE_STROKE * 1.5),
            end=(box_west + clearance - self.__BASE_STROKE * 1.5, box_south - clearance - self.__BASE_STROKE * 1.5),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))
        g_eor.add(self.__dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))
        g_eor.add(self.__dwg.line(
            start=(box_east - clearance + self.__BASE_STROKE * 1.5, box_north + clearance + self.__BASE_STROKE * 1.5),
            end=(box_west + clearance + self.__BASE_STROKE * 1.5, box_south - clearance + self.__BASE_STROKE * 1.5),
            stroke="#FFFFFF", stroke_width=self.__BASE_STROKE))

        g_flashers = g_msi_row.add(self.__dwg.g(id=f"a[{msi_name}]", visibility="hidden"))
        g_flashers.add(self.__dwg.circle(center=(box_west + clearance / 2, box_north + clearance / 2),
                                         r=clearance / 4, fill="yellow"))  # top-left
        g_flashers.add(self.__dwg.circle(center=(box_east - clearance / 2, box_north + clearance / 2),
                                         r=clearance / 4, fill="yellow"))  # top-right
        g_flashers.add(self.__dwg.circle(center=(box_west + clearance / 2, box_south - clearance / 2),
                                         r=clearance / 4, fill="black"))  # bottom-left
        g_flashers.add(self.__dwg.circle(center=(box_east - clearance / 2, box_south - clearance / 2),
                                         r=clearance / 4, fill="black"))  # bottom-right

        for circle in g_flashers.elements[:2]:
            circle.add(self.__dwg.animate("fill", attributeType="XML", from_="yellow", to="black",
                                          id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))
        for circle in g_flashers.elements[-2:]:
            circle.add(self.__dwg.animate("fill", attributeType="XML", from_="black", to="yellow",
                                          id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))

        g_red_ring = g_msi_row.add(self.__dwg.g(id=f"b[{msi_name}]", visibility="hidden"))
        g_red_ring.add(self.__dwg.circle(
            center=center_coords,
            r=box_size * 0.40,
            fill="none", stroke="#FF0000", stroke_width=self.__BASE_STROKE))

    def __display_vergence(self, point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float):
        g_vergence = self.__g_points.add(self.__dwg.g())

        text = self.__dwg.text(f"{point_info.pos_eigs.km} {point_info.obj_eigs['Type']}",
                               insert=(coords[0] + 1 + info_offset, coords[1]),
                               fill="white", font_family="Arial", dominant_baseline="central", font_size=4)

        g_vergence.add(text)
        g_vergence.rotate(rotate_angle, center=coords)

    def __svg_draw_msi_relations(self):
        with open(self.__relation_file, "r") as rel_file:
            lines = rel_file.readlines()

        for line in lines:
            start_msi, relation, end_msi = line.strip().split()
            if start_msi in self.__element_by_id.keys() and end_msi in self.__element_by_id.keys():
                start_pos = self.__get_square_center_coords(start_msi)
                end_pos = self.__get_square_center_coords(end_msi)
                rel_type = relation[-1]  # The last letter is enough to distinguish the colors for visualisation.

                # Draw up to the middle of the relation, allowing for visually checking if both directions are the same.
                mid_pos = ((start_pos[0] + end_pos[0])/2, (start_pos[1] + end_pos[1])/2)
                self.__draw_msi_relation(rel_type, start_pos, mid_pos)

    def __draw_msi_relation(self, rel_type: str, start_pos: tuple, end_pos: tuple):
        self.__g_msi_relations.add(self.__dwg.line(start=start_pos, end=end_pos,
                                                   stroke=self.__RELATION_COLORMAP.get(rel_type, "black"),
                                                   stroke_width=self.__BASE_STROKE * 2))

    def __get_square_center_coords(self, msi: str):
        element, rotation, origin = self.__element_by_id[msi]
        x = element.attribs["x"] + element.attribs["width"] / 2
        y = element.attribs["y"] + element.attribs["height"] / 2
        return self.__rotate_point((x, y), origin, rotation)

    @staticmethod
    def __rotate_point(draw_point, origin, angle_degrees):
        angle_rad = math.radians(angle_degrees)
        x, y = draw_point
        ox, oy = origin
        qx = ox + math.cos(angle_rad) * (x - ox) - math.sin(angle_rad) * (y - oy)
        qy = oy + math.sin(angle_rad) * (x - ox) + math.cos(angle_rad) * (y - oy)
        return qx, qy


def make_name(point_info, nr) -> str:
    """
    Makes MSI name using the MTM2 convention.
    """
    if point_info.pos_eigs.hectoletter:
        return (f"{point_info.pos_eigs.wegnummer}_{point_info.pos_eigs.hectoletter.upper()}:"
                f"{point_info.pos_eigs.km:.3f}:{nr}")
    else:
        return f"{point_info.pos_eigs.wegnummer}{point_info.pos_eigs.rijrichting}:{point_info.pos_eigs.km:.3f}:{nr}"


def make_msi_text(pos_eigs: PositieEigenschappen) -> str:
    """
    Generates the text for display next to an MSI row.
    Args:
        pos_eigs (PositieEigenschappen): Point properties of the MSI registration.
    Returns:
        Name for display, based on point info, containing road number,
        kilometer and driving direction (replaced by hectoletter if present).
    """
    if pos_eigs.hectoletter:
        return f"{pos_eigs.wegnummer} {pos_eigs.km} {pos_eigs.hectoletter}"
    return f"{pos_eigs.wegnummer}  {pos_eigs.km} {pos_eigs.rijrichting}"
