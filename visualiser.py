from road_model import WegModel, ObjectInfo
from msi_relations import MSINetwerk
import svgwrite
from shapely import *
from utils import *
logger = logging.getLogger(__name__)


class SvgMaker:
    
    __C_TRANSPARENT = "#6D876D"
    __C_HIGHLIGHT = "dimgrey"
    __C_ASPHALT = "grey"
    __C_WHITE = "#faf8f5"

    __COLORMAP = {
        "d": "cyan", "u": "cyan",  # Primary
        "s": "magenta",  # Secondary
        "t": "red",  # Taper
        "b": "orange",  # Broadening
        "n": "yellow",  # Narrowing
    }
    
    def __init__(self, wegmodel: WegModel, relation_file_name: str,
                 output_pad: str, formaat: int = 1000, onroad: bool = False):
        self.wegmodel = wegmodel
        self.relation_file = relation_file_name
        self.outfile = output_pad
        self.size = formaat
        self.onroad = onroad
        self.element_by_id = {}

        # Visualiser parameters (constants)
        self.LANE_WIDTH = 3.5

        if onroad:
            self.MSIBOX_SIZE = self.LANE_WIDTH * 0.8
            self.TEXT_SIZE = max(4.0, self.MSIBOX_SIZE * 0.8)
            self.VISUAL_PLAY = self.MSIBOX_SIZE * 0.2
            self.BASE_STROKE = self.MSIBOX_SIZE * 0.07
        else:
            self.MSIBOX_SIZE = 20
            self.TEXT_SIZE = self.MSIBOX_SIZE * 0.6
            self.VISUAL_PLAY = self.MSIBOX_SIZE * 0.2
            self.BASE_STROKE = self.MSIBOX_SIZE * 0.05

        self.TOP_LEFT_X, self.TOP_LEFT_Y = get_coordinates(self.wegmodel.dfl.extent)[2]
        self.BOTTOM_RIGHT_X, self.BOTTOM_RIGHT_Y = get_coordinates(self.wegmodel.dfl.extent)[4]
        self.VIEWBOX_WIDTH = abs(self.TOP_LEFT_X - self.BOTTOM_RIGHT_X)
        self.VIEWBOX_HEIGHT = abs(self.TOP_LEFT_Y - self.BOTTOM_RIGHT_Y)
        self.RATIO = self.VIEWBOX_HEIGHT / self.VIEWBOX_WIDTH

        # Create instances for visualisation
        self.dwg = svgwrite.Drawing(filename=self.outfile,
                                    size=(self.size, self.size * self.RATIO),
                                    profile="full",
                                    id="svg5")  # This specific ID tag is used by JvM script

        # Determine 'layer' order
        self.g_background = self.dwg.add(self.dwg.g(id="background"))
        self.g_road = self.dwg.add(self.dwg.g(id="road"))
        self.g_msi_relations = self.dwg.add(self.dwg.g(id="nametags_MSI"))  # This tag is for visibility toggle in UI
        self.g_points = self.dwg.add(self.dwg.g(id="points"))

        # Visualise the image part by part
        self.visualise_background()
        self.visualise_roads()
        self.visualise_msis()
        self.save_image()

    def visualise_background(self):
        # Background
        self.g_background.add(
            self.dwg.rect(insert=(self.TOP_LEFT_X, self.TOP_LEFT_Y),
                          size=(self.VIEWBOX_WIDTH, self.VIEWBOX_HEIGHT), fill="green"))

    def visualise_roads(self):
        logger.info("Sectiedata visualiseren...")
        for section_id, section_info in self.wegmodel.sections.items():
            self.svg_add_section(section_id, section_info)

    def visualise_msis(self):
        logger.info("Puntdata visualiseren...")
        for point in self.wegmodel.get_points_info("MSI"):
            self.svg_add_point(point)

        logger.info("MSI-relaties visualiseren...")
        self.draw_msi_relations()

    def save_image(self):
        # Adjust viewbox
        self.dwg.viewbox(minx=self.TOP_LEFT_X, miny=self.TOP_LEFT_Y, width=self.VIEWBOX_WIDTH,
                         height=self.VIEWBOX_HEIGHT)

        # Save SVG file
        self.dwg.save(pretty=True, indent=2)

        logger.info("Visualisatie succesvol afgerond.")

    def get_road_color(self, prop: dict) -> str:
        """
        Determines color for road section visualisation based on the provided road properties.
        Args:
            prop (dict): Properties of road section.
        Returns:
            Color name as string.
        """
        if self.determine_gap(prop):
            return self.__C_TRANSPARENT
        elif "Special" in prop.keys():
            return self.__C_HIGHLIGHT
        else:
            return self.__C_ASPHALT

    @staticmethod
    def determine_gap(prop: dict) -> bool:
        """
        Determines whether there is a gap in the lane registrations of a section.
        Args:
            prop (dict): Properties of road section.
        Returns:
            Boolean indicating whether a gap occurs.
        """
        lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int)])
        for lane_number in lane_numbers[:-1]:
            if lane_number + 1 not in prop.keys():
                return True
        return False

    def get_flipped_coords(self, geom: LineString | Point) -> list[tuple]:
        """
        Flips geometries around the top border of the frame and returns the coordinates.
        This is necessary for visualisation, as the RD-coordinate system and the SVG
        coordinate system have a different definition of their y-axis.
        Args:
            geom (LineString or Point): Geometry to be flipped.
        Returns:
            List of coordinates making up the flipped geometry.
        """
        return [(coord[0], self.TOP_LEFT_Y - (coord[1] - self.TOP_LEFT_Y)) for coord in geom.coords]

    def get_offset_coords(self, geom: LineString, offset: float = 0) -> list[tuple]:
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
            return self.get_flipped_coords(geom)
        else:
            offset_geom = offset_curve(geom, offset, join_style="mitre", mitre_limit=5)
            return self.get_flipped_coords(offset_geom)

    def check_points_on_line(self, sid: int) -> list[ObjectInfo]:
        """
        Finds a *vergence point on the section. Assumes there is at most one *vergence
        point per section. In any case, the first one encountered is returned.
        Args:
            sid (int): Section ID to search for.
        Returns:
            Point info of all points on the section in a list
        """
        #
        points_info = []
        for point_info in self.wegmodel.get_points_info():
            if sid in point_info.verw_eigs.sectie_ids and point_info.obj_eigs["Type"] not in ["Signalering"]:
                points_info.append(point_info)
        return points_info

    def get_changed_geometry(self, section_id: int, section_info: ObjectInfo,
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
                                             self.wegmodel.DISTANCE_TOLERANCE)
            point_is_at_line_end = dwithin(Point(line_geom.coords[-1]),
                                           point_info.pos_eigs.geometrie,
                                           self.wegmodel.DISTANCE_TOLERANCE)

            if point_type == "Splitsing" and point_is_at_line_start:
                other_lane_id = list(set(point_info.verw_eigs.uitgaande_secties) - {section_id})[0]
                line_geom = self.move_endpoint(section_info, line_geom, other_lane_id, point_info, True)
            elif point_type == "Samenvoeging" and point_is_at_line_end:
                other_lane_id = list(set(point_info.verw_eigs.ingaande_secties) - {section_id})[0]
                line_geom = self.move_endpoint(section_info, line_geom, other_lane_id, point_info, False)
            elif point_type == "Uitvoeging" and point_is_at_line_start:
                other_lane_id = list(set(point_info.verw_eigs.uitgaande_secties) - {section_id})[0]
                line_geom = self.move_endpoint(section_info, line_geom, other_lane_id, point_info, True)
            elif point_type == "Invoeging" and point_is_at_line_end:
                other_lane_id = list(set(point_info.verw_eigs.ingaande_secties) - {section_id})[0]
                line_geom = self.move_endpoint(section_info, line_geom, other_lane_id, point_info, False)
            else:
                # This is for all cases where a section DOES connect to a *vergence point, but should not be moved.
                continue

        return line_geom

    def move_endpoint(self, this_section_info: ObjectInfo, line_geom: LineString, other_section_id: int,
                      point_info: ObjectInfo, change_start: bool = True):
        other_section_info = self.wegmodel.sections[other_section_id]

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
            displacement = self.LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)

        elif other_is_continuous:
            n_lanes_a = other_section_info.verw_eigs.aantal_hoofdstroken
            n_lanes_b = this_section_info.verw_eigs.aantal_hoofdstroken
            displacement = (self.LANE_WIDTH / 2 * (n_lanes_largest - n_lanes_a)
                            - self.LANE_WIDTH / 2 * (n_lanes_a + n_lanes_b))

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

    def svg_add_section(self, section_id: int, section_info: ObjectInfo):
        points_on_line = self.check_points_on_line(section_id)

        if points_on_line:
            geom = self.get_changed_geometry(section_id, section_info, points_on_line)
        else:
            geom = section_info.pos_eigs.geometrie

        n_main_lanes, n_total_lanes = self.wegmodel.get_n_lanes(section_info.obj_eigs)

        n_main_lanes = section_info.verw_eigs.aantal_hoofdstroken
        n_lanes_left = section_info.verw_eigs.aantal_rijstroken_links
        n_lanes_right = section_info.verw_eigs.aantal_rijstroken_rechts

        if n_main_lanes < 1 or n_total_lanes < 1:
            # These sections are not added. This is fine, because they fall outside the visualisation frame.
            return

        # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
        offset = self.LANE_WIDTH * (n_lanes_left - n_lanes_right) / 2

        asphalt_coords = self.get_offset_coords(geom, offset)
        color = self.get_road_color(section_info.obj_eigs)
        width = self.LANE_WIDTH * n_total_lanes

        self.g_road.add(self.dwg.polyline(points=asphalt_coords, stroke=color, fill="none", stroke_width=width))

        should_have_marking = color in [self.__C_ASPHALT, self.__C_HIGHLIGHT]

        if should_have_marking:
            self.draw_lane_marking(geom, section_info)

    def draw_lane_marking(self, geom: LineString, section_info: ObjectInfo):
        prop = section_info.obj_eigs
        lane_numbers = sorted([nr for nr, lane in prop.items() if isinstance(nr, int)])

        # Offset centered around main lanes. Positive offset distance is on the left side of the LineString.
        marking_offsets = [(self.LANE_WIDTH * section_info.verw_eigs.aantal_hoofdstroken) / 2
                           + self.LANE_WIDTH * section_info.verw_eigs.aantal_rijstroken_links
                           - self.LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

        first_lane_nr = lane_numbers[0]
        last_lane_nr = lane_numbers[-1]
        next_lane = None

        # Exclude puntstuk from counting as the last lane
        if prop[last_lane_nr] == "Puntstuk":
            last_lane_nr = lane_numbers[-2]

        # Add first solid marking (leftmost), except when the first lane is a vluchtstrook.
        line_coords = self.get_offset_coords(geom, marking_offsets.pop(0))
        if prop[first_lane_nr] not in ["Vluchtstrook"]:
            self.draw_markerline(line_coords)
        # Also add puntstuk if it is the very first registration
        if prop[first_lane_nr] == "Puntstuk":
            if section_info.verw_eigs.vergentiepunt_start:
                self.draw_markerline(line_coords, "Punt-start", direction=-1)
            elif section_info.verw_eigs.vergentiepunt_einde:
                self.draw_markerline(line_coords, "Punt-einde", direction=-1)

        # Add middle markings. All of these markings have a this_lane and a next_lane
        for this_lane_number in lane_numbers[:-1]:
            next_lane_number = this_lane_number + 1

            this_lane = prop[this_lane_number]
            next_lane = prop[next_lane_number]

            # Puntstuk has already been drawn
            if this_lane == "Puntstuk":
                continue

            # A puntstuk that is not the first lane, is the final lane.
            if next_lane == "Puntstuk":
                line_coords = self.get_offset_coords(geom, marking_offsets.pop(0))
                self.draw_markerline(line_coords)
                if section_info.verw_eigs.vergentiepunt_start:
                    self.draw_markerline(line_coords, "Punt-start", direction=1)
                elif section_info.verw_eigs.vergentiepunt_einde:
                    self.draw_markerline(line_coords, "Punt-einde", direction=1)
                break

            # Puntstuk cases have been handled, now the normal cases.
            line_coords = self.get_offset_coords(geom, marking_offsets.pop(0))

            # An emergency lane is demarcated with a solid line.
            if this_lane == "Vluchtstrook" or next_lane == "Vluchtstrook":
                self.draw_markerline(line_coords)

            # A plus lane is demarcated with a 9-3 dashed line.
            elif this_lane == "Plusstrook":
                self.draw_markerline(line_coords, "Streep-9-3")

            # If the next lane is a samenvoeging, use normal dashed lane marking.
            elif next_lane == "Samenvoeging":
                self.draw_markerline(line_coords, "Streep-3-9")

            # A rush hour lane (on the final lane) has special lines.
            elif next_lane == "Spitsstrook" and next_lane_number == last_lane_nr:
                self.draw_markerline(line_coords)

            # All other lanes are separated by dashed lines.
            elif this_lane == next_lane:
                self.draw_markerline(line_coords, "Streep-3-9")

            # If the lane types are not the same, block markings are used.
            else:
                self.draw_markerline(line_coords, "Blok")

        # Add last solid marking (rightmost), except when the last lane is a vluchtstrook or puntstuk.
        # Spitsstrook has special lane marking.
        line_coords = self.get_offset_coords(geom, marking_offsets.pop(0))
        if next_lane == "Spitsstrook":
            self.draw_markerline(line_coords, "Dun")
        elif next_lane not in ["Vluchtstrook", "Puntstuk"]:
            self.draw_markerline(line_coords)

    def draw_markerline(self, coords: list[tuple], linetype: str = "full", direction: int = 1):
        if linetype == "Streep-3-9":
            self.draw_line(coords, 0.4, "3 9")
        elif linetype == "Streep-9-3":
            self.draw_line(coords, 0.4, "9 3")
        elif linetype == "Blok":
            self.draw_line(coords, 0.6, "0.8 4")
        elif linetype == "Punt-start" or linetype == "Punt-einde":
            self.draw_triangle(coords, linetype, direction)
            self.draw_line(coords, 0.4)
        elif linetype == "Dun":
            self.draw_line(coords, 0.2)
        else:
            self.draw_line(coords, 0.4)

    def draw_line(self, coords: list[tuple], width: float, dasharray: str = ""):
        if dasharray:
            line = self.dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width,
                                     stroke_dasharray=dasharray)
        else:
            line = self.dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width)
        self.g_road.add(line)

    def draw_triangle(self, coords: list[tuple], linetype: str, direction: int = 1):
        triangle_end = coords[-1] if linetype == "Punt-start" else coords[0]

        vec = [coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]]
        mag = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        third_point = (triangle_end[0] + self.LANE_WIDTH * direction * -vec[1] / mag,
                       triangle_end[1] + self.LANE_WIDTH * direction * vec[0] / mag)
        all_points = coords + [third_point]

        triangle = self.dwg.polygon(points=all_points, fill=self.__C_WHITE)
        self.g_road.add(triangle)

    def svg_add_point(self, point_info: ObjectInfo):
        coords = self.get_flipped_coords(point_info.pos_eigs.geometrie)[0]
        # TODO: Update these calculations so they are uniform with the new approach
        info_offset = self.LANE_WIDTH * (point_info.verw_eigs.aantal_stroken + point_info.verw_eigs.aantal_stroken -
                                         point_info.verw_eigs.aantal_hoofdstroken) / 2
        rotate_angle = 90 - point_info.verw_eigs.lokale_hoek

        if point_info.obj_eigs["Type"] == "Signalering":
            if self.onroad:
                self.display_MSI_onroad(point_info, coords, rotate_angle)
            else:
                self.display_MSI_roadside(point_info, coords, info_offset, rotate_angle)
        else:
            self.display_vergence(point_info, coords, info_offset, rotate_angle)

    def display_MSI_roadside(self, point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float):
        g_msi_row = self.g_points.add(self.dwg.g())
        hecto_offset = 0 if point_info.pos_eigs.hectoletter in ["", "w", "h"] else self.LANE_WIDTH * 25
        displacement = 0

        for nr in point_info.obj_eigs["Rijstrooknummers"]:
            msi_name = make_name(point_info, nr)
            displacement = (info_offset + self.VISUAL_PLAY + (nr - 1) *
                            (self.VISUAL_PLAY + self.MSIBOX_SIZE) + hecto_offset)
            box_pos = (coords[0] + displacement, coords[1] - self.MSIBOX_SIZE / 2)
            square = self.draw_msi(box_pos)
            g_msi_row.add(square)
            self.element_by_id[msi_name] = square, rotate_angle, coords

            # Extra elements
            box_center = (coords[0] + displacement + self.MSIBOX_SIZE / 2, coords[1])
            self.draw_all_legends(g_msi_row, msi_name, box_pos, box_center, self.MSIBOX_SIZE)

        text_coords = (coords[0] + displacement + self.MSIBOX_SIZE * 1.3, coords[1])
        
        g_msi_text = self.draw_msi_text(point_info, text_coords, rotate_angle)
        g_msi_row.add(g_msi_text)
        g_msi_row.rotate(rotate_angle, center=coords)

    def display_MSI_onroad(self, point_info: ObjectInfo, coords: tuple, rotate_angle: float):
        g_msi_row = self.g_points.add(self.dwg.g())
        play = (self.LANE_WIDTH - self.MSIBOX_SIZE)/2
        displacement = 0

        for nr in point_info.obj_eigs["Rijstrooknummers"]:
            msi_name = make_name(point_info, nr)
            displacement = self.LANE_WIDTH * (nr - 1) - point_info.verw_eigs.aantal_hoofdstroken * self.LANE_WIDTH / 2
            box_pos = (coords[0] + displacement + play, coords[1] - self.MSIBOX_SIZE / 2)
            square = self.draw_msi(box_pos)
            g_msi_row.add(square)
            self.element_by_id[msi_name] = square, rotate_angle, coords

            # Extra elements
            box_center = (coords[0] + displacement + play + self.MSIBOX_SIZE / 2, coords[1])
            self.draw_all_legends(g_msi_row, msi_name, box_pos, box_center, self.MSIBOX_SIZE)

        text_coords = (coords[0] + 2 + displacement + self.MSIBOX_SIZE, coords[1])
        
        g_msi_text = self.draw_msi_text(point_info, text_coords, rotate_angle)
        g_msi_row.add(g_msi_text)
        g_msi_row.rotate(rotate_angle, center=coords)

    def draw_msi(self, box_pos):
        return self.dwg.rect(insert=box_pos,
                             size=(self.MSIBOX_SIZE, self.MSIBOX_SIZE),
                             fill="#1e1b17", stroke="black", stroke_width=self.BASE_STROKE,
                             onmouseover="evt.target.setAttribute('fill', 'darkslategrey');",
                             onmouseout="evt.target.setAttribute('fill', '#1e1b17');")
    
    def draw_msi_text(self, point_info, text_coords, rotate_angle):
        g_text = self.dwg.g()
        anchorpoint = "start" if -90 < rotate_angle < 90 else "end"
        text = self.dwg.text(make_text_hecto(point_info.pos_eigs.km,
                                             point_info.pos_eigs.rijrichting,
                                             point_info.pos_eigs.hectoletter),
                             insert=text_coords, text_anchor=anchorpoint, font_size=self.TEXT_SIZE,
                             fill="white", font_family="Arial", dominant_baseline="central")
        g_text.add(text)
        g_text.rotate(-rotate_angle, center=text_coords)
        return g_text

    def draw_all_legends(self, g_msi_row: svgwrite.container.Group, msi_name: str,
                         box_coords: tuple, center_coords: tuple, box_size: float):
        box_west = box_coords[0]
        box_north = box_coords[1]
        box_east = box_west + box_size
        box_south = box_north + box_size
        clearance = box_size*0.2

        g_50 = g_msi_row.add(self.dwg.g(id=f"e[{msi_name}]", visibility="hidden"))
        g_50.add(self.dwg.text(
            "50", insert=center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_70 = g_msi_row.add(self.dwg.g(id=f"g[{msi_name}]", visibility="hidden"))
        g_70.add(self.dwg.text(
            "70", insert=center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_80 = g_msi_row.add(self.dwg.g(id=f"h[{msi_name}]", visibility="hidden"))
        g_80.add(self.dwg.text(
            "80", insert=center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_90 = g_msi_row.add(self.dwg.g(id=f"i[{msi_name}]", visibility="hidden"))
        g_90.add(self.dwg.text(
            "90", insert=center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            text_anchor="middle", dominant_baseline="middle"))

        g_100 = g_msi_row.add(self.dwg.g(id=f"j[{msi_name}]", visibility="hidden"))
        g_100.add(self.dwg.text(
            "100", insert=center_coords, fill="white", font_family="Arial narrow", font_size=box_size*0.60,
            letter_spacing="-0.5", text_anchor="middle", dominant_baseline="middle"))

        g_overruling_blank = g_msi_row.add(self.dwg.g(id=f"o[{msi_name}]", visibility="hidden"))
        g_overruling_blank.add(self.dwg.rect(insert=box_coords,
                                             size=(self.MSIBOX_SIZE, self.MSIBOX_SIZE),
                                             fill="#1e1b17", stroke="none"))

        g_red_cross = g_msi_row.add(self.dwg.g(id=f"x[{msi_name}]", visibility="hidden"))
        g_red_cross.add(self.dwg.line(
            start=(box_west + clearance, box_north + clearance),
            end=(box_east - clearance, box_south - clearance),
            stroke="#FF0000", stroke_width=self.BASE_STROKE))  # \
        g_red_cross.add(self.dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance, box_south - clearance),
            stroke="#FF0000", stroke_width=self.BASE_STROKE))  # /

        g_green_arrow = g_msi_row.add(self.dwg.g(id=f"y[{msi_name}]", visibility="hidden"))
        g_green_arrow.add(self.dwg.line(
            start=(box_west + box_size / 2, box_north + clearance / 2),
            end=(box_west + box_size / 2, box_south - clearance * 1.5),
            stroke="#00FF00", stroke_width=self.BASE_STROKE))  # |
        g_green_arrow.add(self.dwg.line(
            start=(box_west + box_size / 2 + math.sqrt(self.BASE_STROKE / 2) / 2, box_south - clearance / 2),
            end=(box_west + clearance + math.sqrt(self.BASE_STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
            stroke="#00FF00", stroke_width=self.BASE_STROKE))  # \
        g_green_arrow.add(self.dwg.line(
            start=(box_west + box_size / 2 - math.sqrt(self.BASE_STROKE / 2) / 2, box_south - clearance / 2),
            end=(box_east - clearance - math.sqrt(self.BASE_STROKE / 2) / 2, box_south - box_size / 2 + clearance / 2),
            stroke="#00FF00", stroke_width=self.BASE_STROKE))  # /

        g_left_arrow = g_msi_row.add(self.dwg.g(id=f"l[{msi_name}]", visibility="hidden"))
        g_left_arrow.add(self.dwg.line(
            start=(box_west + clearance - self.BASE_STROKE / 2, box_south - clearance),
            end=(box_east - clearance * 1.75, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # _
        g_left_arrow.add(self.dwg.line(
            start=(box_west + clearance, box_south - clearance + self.BASE_STROKE / 2),
            end=(box_west + clearance, box_north + clearance * 1.75),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # |
        g_left_arrow.add(self.dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance * 1.5, box_south - clearance * 1.5),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # /

        g_right_arrow = g_msi_row.add(self.dwg.g(id=f"r[{msi_name}]", visibility="hidden"))
        g_right_arrow.add(self.dwg.line(
            start=(box_east - clearance + self.BASE_STROKE / 2, box_south - clearance),
            end=(box_west + clearance * 1.75, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # _
        g_right_arrow.add(self.dwg.line(
            start=(box_east - clearance, box_south - clearance + self.BASE_STROKE / 2),
            end=(box_east - clearance, box_north + clearance * 1.75),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # |
        g_right_arrow.add(self.dwg.line(
            start=(box_west + clearance, box_north + clearance),
            end=(box_east - clearance * 1.5, box_south - clearance * 1.5),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))  # \

        g_eor = g_msi_row.add(self.dwg.g(id=f"z[{msi_name}]", visibility="hidden"))
        g_eor.add(self.dwg.circle(
            center=center_coords,
            r=box_size * 0.45,
            fill="none", stroke="#FFFFFF", stroke_width=self.BASE_STROKE))
        g_eor.add(self.dwg.line(
            start=(box_east - clearance - self.BASE_STROKE * 1.5, box_north + clearance - self.BASE_STROKE * 1.5),
            end=(box_west + clearance - self.BASE_STROKE * 1.5, box_south - clearance - self.BASE_STROKE * 1.5),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))
        g_eor.add(self.dwg.line(
            start=(box_east - clearance, box_north + clearance),
            end=(box_west + clearance, box_south - clearance),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))
        g_eor.add(self.dwg.line(
            start=(box_east - clearance + self.BASE_STROKE * 1.5, box_north + clearance + self.BASE_STROKE * 1.5),
            end=(box_west + clearance + self.BASE_STROKE * 1.5, box_south - clearance + self.BASE_STROKE * 1.5),
            stroke="#FFFFFF", stroke_width=self.BASE_STROKE))

        g_flashers = g_msi_row.add(self.dwg.g(id=f"a[{msi_name}]", visibility="hidden"))
        g_flashers.add(self.dwg.circle(center=(box_west + clearance / 2, box_north + clearance / 2),
                                       r=clearance / 4, fill="yellow"))  # top-left
        g_flashers.add(self.dwg.circle(center=(box_east - clearance / 2, box_north + clearance / 2),
                                       r=clearance / 4, fill="yellow"))  # top-right
        g_flashers.add(self.dwg.circle(center=(box_west + clearance / 2, box_south - clearance / 2),
                                       r=clearance / 4, fill="black"))  # bottom-left
        g_flashers.add(self.dwg.circle(center=(box_east - clearance / 2, box_south - clearance / 2),
                                       r=clearance / 4, fill="black"))  # bottom-right

        for circle in g_flashers.elements[:2]:
            circle.add(self.dwg.animate("fill", attributeType="XML", from_="yellow", to="black",
                                        id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))
        for circle in g_flashers.elements[-2:]:
            circle.add(self.dwg.animate("fill", attributeType="XML", from_="black", to="yellow",
                                        id="anim", dur="3s", repeatCount="indefinite", calcMode="discrete"))

        g_red_ring = g_msi_row.add(self.dwg.g(id=f"b[{msi_name}]", visibility="hidden"))
        g_red_ring.add(self.dwg.circle(
            center=center_coords,
            r=box_size * 0.40,
            fill="none", stroke="#FF0000", stroke_width=self.BASE_STROKE))

    def display_vergence(self, point_info: ObjectInfo, coords: tuple, info_offset: float, rotate_angle: float):
        g_vergence = self.g_points.add(self.dwg.g())

        text = self.dwg.text(f"{point_info.pos_eigs.km} {point_info.obj_eigs['Type']}",
                             insert=(coords[0] + 1 + info_offset, coords[1]),
                             fill="white", font_family="Arial", dominant_baseline="central", font_size=4)

        g_vergence.add(text)
        g_vergence.rotate(rotate_angle, center=coords)

    def draw_msi_relations(self):
        with open(self.relation_file, "r") as rel_file:
            lines = rel_file.readlines()

        for line in lines:
            start_msi, relation, end_msi = line.strip().split()
            if start_msi in self.element_by_id.keys() and end_msi in self.element_by_id.keys():
                start_pos = self.get_square_center_coords(start_msi)
                end_pos = self.get_square_center_coords(end_msi)
                # Idea: Draw only up to the middle of the relation? To visually check if both sides are the same!
                # The final letter of the relation type is enough to distinguish the colors for visualisation.
                self.draw_msi_relation(relation[-1], start_pos, end_pos)

    def draw_msi_relation(self, rel_type: str, start_pos: tuple, end_pos: tuple):
        self.g_msi_relations.add(self.dwg.line(start=start_pos, end=end_pos,
                                               stroke=self.__COLORMAP[rel_type], stroke_width=self.BASE_STROKE * 2))

    def get_square_center_coords(self, msi: str):
        element, rotation, origin = self.element_by_id[msi]
        x = element.attribs["x"] + element.attribs["width"] / 2
        y = element.attribs["y"] + element.attribs["height"] / 2
        return rotate_point((x, y), origin, rotation)


def rotate_point(draw_point, origin, angle_degrees):
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
                f"{point_info.pos_eigs.km}:{nr}")
    else:
        return f"{point_info.pos_eigs.wegnummer}{point_info.pos_eigs.rijrichting}:{point_info.pos_eigs.km}:{nr}"


def make_text_hecto(km: float, rijrichting: str, letter: str | None) -> str:
    if letter:
        return f"{km} {letter}"
    return f"{km} {rijrichting}"
