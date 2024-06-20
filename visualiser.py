from road_model import WegModel, ObjectInfo, PositieEigenschappen
from msi_relations import MSINetwerk, MSIRow
import svgwrite
import os
from enum import Enum
from shapely import *
from utils import *

logger = logging.getLogger(__name__)

# Stroken
GEEN_STROOK = "Geen-strook"
VLUCHTSTROOK = "Vluchtstrook"
SPITSSTROOK_LINKS = "Spitsstrook-links"
RIJSTROOK = "Rijstrook"
SPLITSING = "Splitsing"
SAMENVOEGING = "Samenvoeging"
INVOEGSTROOK = "Invoegstrook"
UITRIJSTROOK = "Uitrijstrook"
WEEFSTROOK = "Weefstrook"
SPITSSTROOK_RECHTS_NIET_LAATSTE = "Spitsstrook-rechts-niet-laatste"
SPITSSTROOK_RECHTS_LAATSTE = "Spitsstrook-rechts-laatste"

# Strepen
KANTSTREEP = 100
BLOKSTREEP = 101
SMALLE_KANTSTREEP = 102
DEELSTREEP_3_9 = 103
DEELSTREEP_9_3 = 104
GEEN_STREEP = 105
PUNTSTUK_START = 106
PUNTSTUK_EINDE = 107
PUNTSTUK_BREED = 108

markeringen = {
    GEEN_STROOK: {
        VLUCHTSTROOK: GEEN_STREEP,
        SPITSSTROOK_LINKS: KANTSTREEP,
        RIJSTROOK: KANTSTREEP,
        SPLITSING: KANTSTREEP,
        UITRIJSTROOK: KANTSTREEP,
    },
    VLUCHTSTROOK: {
        GEEN_STROOK: GEEN_STREEP,
        RIJSTROOK: KANTSTREEP,
    },
    SPITSSTROOK_LINKS: {
        RIJSTROOK: DEELSTREEP_9_3,
    },
    RIJSTROOK: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        RIJSTROOK: DEELSTREEP_3_9,
        SPLITSING: BLOKSTREEP,
        SAMENVOEGING: BLOKSTREEP,
        INVOEGSTROOK: BLOKSTREEP,
        UITRIJSTROOK: BLOKSTREEP,
        WEEFSTROOK: BLOKSTREEP,
        SPITSSTROOK_RECHTS_NIET_LAATSTE: BLOKSTREEP,
        SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    SPLITSING: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        RIJSTROOK: BLOKSTREEP,
        SPLITSING: DEELSTREEP_3_9,
        INVOEGSTROOK: BLOKSTREEP,
        UITRIJSTROOK: BLOKSTREEP,
        WEEFSTROOK: BLOKSTREEP,
        SPITSSTROOK_RECHTS_NIET_LAATSTE: BLOKSTREEP,
        SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    SAMENVOEGING: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        SAMENVOEGING: DEELSTREEP_3_9,
        INVOEGSTROOK: BLOKSTREEP,
        UITRIJSTROOK: BLOKSTREEP,
        WEEFSTROOK: BLOKSTREEP,
        SPITSSTROOK_RECHTS_NIET_LAATSTE: BLOKSTREEP,
        SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    INVOEGSTROOK: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        INVOEGSTROOK: DEELSTREEP_3_9,
        # SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    UITRIJSTROOK: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        RIJSTROOK: BLOKSTREEP,
        UITRIJSTROOK: DEELSTREEP_3_9,
        # SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    WEEFSTROOK: {
        GEEN_STROOK: KANTSTREEP,
        VLUCHTSTROOK: KANTSTREEP,
        WEEFSTROOK: DEELSTREEP_3_9,
        # SPITSSTROOK_RECHTS_LAATSTE: KANTSTREEP,
    },
    SPITSSTROOK_RECHTS_NIET_LAATSTE: {
        INVOEGSTROOK: BLOKSTREEP,
        UITRIJSTROOK: BLOKSTREEP,
        WEEFSTROOK: BLOKSTREEP,
    },
    SPITSSTROOK_RECHTS_LAATSTE: {
        GEEN_STROOK: SMALLE_KANTSTREEP,
    },
}


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
        self.__g_road_info = self.__dwg.add(self.__dwg.g(id="road_info"))

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
        ids = []
        for section_id, section_info in self.__wegmodel.sections.items():
            added = self.__svg_draw_section(section_id, section_info)
            if added:
                ids.append(section_id)

        script_content = """
        function showInfoBox(id) {
            document.getElementById('SECTION_INFO_' + id).setAttribute('visibility', 'visible');
        }
        function hideInfoBox(id) {
            document.getElementById('SECTION_INFO_' + id).setAttribute('visibility', 'hidden');
        }
        """
        script_element = self.__dwg.script(content=script_content, type="application/ecmascript")
        self.__dwg.defs.add(script_element)

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
        if lane_nr == 0:
            leftmost_marking = True
            lane_nr = 1
        else:
            leftmost_marking = False

        if not lane_nr or (lane_nr not in section_info.verw_eigs.start_kenmerk
                           and lane_nr not in section_info.verw_eigs.einde_kenmerk):
            return geom

        # Move first point of line
        if (lane_nr in section_info.verw_eigs.start_kenmerk and (lane_nr != 1 or leftmost_marking)
                and section_info.verw_eigs.start_kenmerk[lane_nr] == "Uitrijstrook"):
            change_start = True
            point_to_displace = geom.coords[0]
            id_upstream = section_info.verw_eigs.sectie_stroomopwaarts
            other_geom = self.__wegmodel.sections[id_upstream].pos_eigs.geometrie
            delta_x = other_geom.coords[-2][0] - geom.coords[1][0]
            delta_y = other_geom.coords[-2][1] - geom.coords[1][1]
            # For the leftmost marking, the direction should be flipped.
            if not leftmost_marking:
                delta_x = -delta_x
                delta_y = -delta_y

        # Move last point of line
        elif (lane_nr in section_info.verw_eigs.einde_kenmerk and
                section_info.verw_eigs.einde_kenmerk[lane_nr] == "Invoegstrook"):
            change_start = False
            point_to_displace = geom.coords[-1]
            id_downstream = section_info.verw_eigs.sectie_stroomafwaarts
            other_geom = self.__wegmodel.sections[id_downstream].pos_eigs.geometrie
            delta_x = other_geom.coords[1][0] - geom.coords[-2][0]
            delta_y = other_geom.coords[1][1] - geom.coords[-2][1]
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

        if this_is_continuous and other_is_continuous:
            logger.warning(f"Twee secties met puntstuk bij {point_info.pos_eigs}\n{this_section_info}\n{other_section_info}")
            return line_geom
        if not (this_is_continuous or other_is_continuous):
            logger.warning(f"Geen sectie met puntstuk bij {point_info.pos_eigs}\n{this_section_info}\n{other_section_info}")
            return line_geom

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

    def __svg_draw_section_info(self, section_id: int, section_info: ObjectInfo):
        origin = self.__get_flipped_coords(line_interpolate_point(
            section_info.pos_eigs.geometrie, 0.5, normalized=True))[0]
        lines = make_info_text(section_info)
        height = 6 * (len(lines) + 1)

        g_infobox = self.__g_road_info.add(self.__dwg.g(id=f"SECTION_INFO_{section_id}", visibility="hidden",
                                                        onmouseover=f"showInfoBox({section_id})",
                                                        onmouseout=f"hideInfoBox({section_id})"))

        indicator_circle = self.__dwg.ellipse(center=(origin[0], origin[1]), r=(3, 3), fill="black")
        textbox = self.__dwg.rect(insert=(origin[0], origin[1]), size=(120, height),
                                  fill="white", stroke="black", stroke_width=self.__BASE_STROKE)
        g_infobox.add(indicator_circle)
        g_infobox.add(textbox)

        for nr, line in enumerate(lines):
            text = self.__dwg.text(line,
                                   insert=(origin[0]+2, origin[1]+4.5+6*nr), font_size=self.__TEXT_SIZE/2,
                                   fill="black", font_family="Arial", dominant_baseline="central")
            g_infobox.add(text)

    def __svg_draw_section(self, section_id: int, section_info: ObjectInfo) -> bool:
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
            return False

        # Offset centered around normal lanes. Positive offset distance is on the left side of the line.
        offset = self.__LANE_WIDTH * (n_lanes_left - n_lanes_right) / 2

        asphalt_coords = self.__get_offset_coords(section_info, adjusted_geom, offset)
        color = self.__get_road_color(section_info)
        width = self.__LANE_WIDTH * n_total_lanes

        self.__g_road.add(
            self.__dwg.polyline(
                id=f"SECTION_{section_id}",
                points=asphalt_coords, stroke=color, fill="none", stroke_width=width,
                onmouseover=f"showInfoBox({section_id})", onmouseout=f"hideInfoBox({section_id})"
            )
        )

        should_have_marking = color not in [self.__C_TRANSPARENT]

        if should_have_marking:
            self.__determine_lane_marking(section_info, adjusted_geom)

        self.__svg_draw_section_info(section_id, section_info)
        return True

    def __determine_lane_marking(self, section_info: ObjectInfo, geom: LineString):
        lane_numbers = sorted([nr for nr, lane in section_info.obj_eigs.items() if isinstance(nr, int)])

        if self.__wegmodel.find_gap(lane_numbers):
            return  # Lane markings cannot be drawn in this case.

        # Offset centered around main lanes. Positive offset distance is on the left side of the LineString.
        marking_offsets = [(self.__LANE_WIDTH * section_info.verw_eigs.aantal_hoofdstroken) / 2
                           + self.__LANE_WIDTH * section_info.verw_eigs.aantal_rijstroken_links
                           - self.__LANE_WIDTH * i for i in range(len(lane_numbers) + 1)]

        # Ensure there is a 'lane number' for the side of the road.
        lane_numbers.insert(0, min(lane_numbers)-1)

        #logger.debug(f"Wegmarkering wordt uitgewerkt voor: {section_info}")
        for lane_number in lane_numbers:
            line_coords = self.__get_offset_coords(section_info, geom, marking_offsets.pop(0), lane_number)

            # Determine lane names left and right of the marking
            left_lane_type = self.__determine_lane_name(section_info.obj_eigs, lane_number)
            right_lane_type = self.__determine_lane_name(section_info.obj_eigs, lane_number + 1)

            if left_lane_type == GEEN_STROOK and right_lane_type == GEEN_STROOK:
                continue

            if left_lane_type == "Puntstuk" or right_lane_type == "Puntstuk":
                self.__handle_puntstuk(section_info, line_coords, right_lane_type)
                if right_lane_type == "Puntstuk":
                    break
                continue

            #logger.debug(f"Lijn tussen {left_lane_type} en {right_lane_type}")
            lane_marking_type = markeringen[left_lane_type][right_lane_type]
            self.__draw_markerline(line_coords, lane_marking_type)

    @staticmethod
    def __determine_lane_name(lanes: dict, lane_number: int) -> str:
        if lane_number not in lanes:
            return GEEN_STROOK
        elif lanes[lane_number] == "Spitsstrook":
            if lane_number == 1:
                return SPITSSTROOK_LINKS
            elif lane_number + 1 not in lanes:
                return SPITSSTROOK_RECHTS_LAATSTE
            else:
                return SPITSSTROOK_RECHTS_NIET_LAATSTE
        else:
            return lanes[lane_number]

    def __handle_puntstuk(self, section_info, line_coords, right_lane_type):
        expansion_direction = 1 if right_lane_type == "Puntstuk" else -1

        if section_info.verw_eigs.vergentiepunt_start:
            self.__draw_markerline(line_coords, PUNTSTUK_START, direction=expansion_direction)
        elif section_info.verw_eigs.vergentiepunt_einde:
            self.__draw_markerline(line_coords, PUNTSTUK_EINDE, direction=expansion_direction)
        else:
            self.__draw_markerline(line_coords, PUNTSTUK_BREED)

    def __draw_markerline(self, coords: list[tuple], linetype: int, direction: int = 1):
        if linetype == KANTSTREEP:
            self.__draw_line(coords, 0.4)
        elif linetype == BLOKSTREEP:
            self.__draw_line(coords, 0.6, "0.8 4")
        elif linetype == SMALLE_KANTSTREEP:
            self.__draw_line(coords, 0.2)
        elif linetype == DEELSTREEP_3_9:
            self.__draw_line(coords, 0.4, "3 9")
        elif linetype == DEELSTREEP_9_3:
            self.__draw_line(coords, 0.4, "9 3")
        elif linetype == PUNTSTUK_START or linetype == PUNTSTUK_EINDE:
            self.__draw_triangle(coords, linetype, direction)
            self.__draw_line(coords, 0.4)
        elif linetype == PUNTSTUK_BREED:
            offset_geom = offset_curve(LineString(coords), self.__LANE_WIDTH/2)
            self.__draw_line([(coord[0], coord[1]) for coord in offset_geom.coords], self.__LANE_WIDTH)
            self.__draw_line(coords, 0.4)
        elif linetype == GEEN_STREEP:
            return
        else:
            logger.warning(f"Line could not be drawn!!")

    def __draw_line(self, coords: list[tuple], width: float, dasharray: str = ""):
        if dasharray:
            line = self.__dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width,
                                       stroke_dasharray=dasharray)
        else:
            line = self.__dwg.polyline(points=coords, fill="none", stroke=self.__C_WHITE, stroke_width=width)
        self.__g_road.add(line)

    def __draw_triangle(self, coords: list[tuple], linetype: int, direction: int = 1):
        triangle_end = coords[-1] if linetype == PUNTSTUK_START else coords[0]

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
        if msi_row.info.pos_eigs.hectoletter in ["", "w"]:
            hecto_offset = 0
        elif msi_row.info.pos_eigs.hectoletter in ["n"]:
            hecto_offset = self.__LANE_WIDTH * 40
        else:
            hecto_offset = self.__LANE_WIDTH * 25
        displacement = 0

        for nr in msi_row.rijstrooknummers:
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

                # Draw up to the middle of the relation, allowing for visually checking relation direction.
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


def make_info_text(section_info: ObjectInfo) -> list[str]:
    lane_keys = sorted([key for key in section_info.obj_eigs.keys() if isinstance(key, int)])
    other_keys = sorted([key for key in section_info.obj_eigs.keys() if not isinstance(key, int)])
    return ([f"Sectie {section_info.pos_eigs.wegnummer} "
             f"{section_info.pos_eigs.rijrichting} {section_info.pos_eigs.hectoletter} "
             f"van {section_info.pos_eigs.km[0]} tot {section_info.pos_eigs.km[1]} km", "Eigenschappen:"] +
            [f"{key}: {section_info.obj_eigs[key]}" for key in lane_keys] +
            [f"{key}: {section_info.obj_eigs[key]}" for key in other_keys])
            # + [f"Start kenmerk: {section_info.verw_eigs.start_kenmerk}",
            #    f"Einde kenmerk: {section_info.verw_eigs.einde_kenmerk}"])
