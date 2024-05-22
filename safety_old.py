from road_model import WegModel, ObjectInfo
from utils import *
from shapely import *
logger = logging.getLogger(__name__)

# This is an old version of the file.

AANVRAAG = 200
WERKVAK = 201
VEILIGHEIDSRUIMTE = 202
WERKRUIMTE = 203

AFZETTING_BAKENS = 300
AFZETTING_BARRIER_LAGER_DAN_80CM = 301
AFZETTING_BARRIER_HOGER_DAN_80CM = 302


class Oppervlak:

    __BREEDTE_BARRIER = 0.50  # Schatting
    __BREEDTE_BAKENS = 0.30  # Schatting

    __TUSSENRUIMTE = {
        AFZETTING_BAKENS: {VEILIGHEIDSRUIMTE: 0.5 * __BREEDTE_BAKENS, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_LAGER_DAN_80CM: {VEILIGHEIDSRUIMTE: 0.5 * __BREEDTE_BARRIER, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_HOGER_DAN_80CM: {VEILIGHEIDSRUIMTE: 0.5 * __BREEDTE_BARRIER, WERKRUIMTE: 0},
    }

    __SURFACE_NAMES = {
        AANVRAAG: "Aanvraag",
        WERKVAK: "Werkvak",
        VEILIGHEIDSRUIMTE: "Veiligheidsruimte",
        WERKRUIMTE: "Werkruimte",
    }

    def __init__(self, parent) -> None:
        self.parent = parent
        self.original_request = parent.request

        self.width_offset = self.__TUSSENRUIMTE.get(self.original_request.demarcation, None).get(self.parent.surf_type, 0)

        self.edge_left = self.parent.edge_left
        self.edge_right = self.parent.edge_right

        self.adjust_edges()

        self.km = self.parent.km  # TODO: Adjust.

        self.log_surface()

    def adjust_edges(self):
        # self.edge_left[1] = self.edge_left[1] + self.width_offset
        self.edge_right = (self.edge_right[0], self.edge_right[1] - self.width_offset)

    def log_surface(self):
        logger.info(f"Oppervlak '{self.__SURFACE_NAMES.get(self.parent.surf_type, 'ONBEKEND')}' gemaakt "
                    f"aan kant {self.original_request.roadside}, "
                    f"van {self.parent.km[0]} tot {self.parent.km[1]}, "
                    f"met breedte {self.edge_left} {self.edge_right}.")


class Aanvraag(Oppervlak):

    # Source: "WIU 2020 - Werken op autosnelwegen 03-10-2023 Rijkswaterstaat"
    __SPHERE_OF_INFLUENCE = {
        130: 13,  # maximum velocity in km/h -> sphere of influence in m
        120: 13,
        100: 10,
        90: 10,
        80: 6,
        70: 6,
        50: 4.5
    }

    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 rand_links: tuple = None, rand_rechts: tuple = None,
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:

        assert rand_links or rand_rechts, "Specificeer minstens één eis."

        self.request = self
        self.surf_type = AANVRAAG
        self.color = "brown"

        self.roadmodel = wegmodel
        self.roadside = wegkant
        self.km = [km_start, km_end]
        self.hectoletter = hectoletter

        self.edge_left = rand_links
        self.edge_right = rand_rechts

        self.max_v = maximumsnelheid
        self.under_24h = korter_dan_24h
        self.demarcation = afzetting

        super().__init__(self)

        self.sections = self.roadmodel.get_section_info_by_bps(km=self.km, side=self.roadside, hecto=self.hectoletter)
        if not self.sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.km} {self.roadside} {self.hectoletter}")

        self.geometry = self.__combine_and_trim_geoms()

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_info = self.sections[0]

        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        if not self.sphere_of_influence:
            logger.warning(f"Sphere of influence not defined for following speed: "
                           f"{self.road_info.obj_eigs['Maximumsnelheid']}")

        self.__make_werkruimte()

    def __get_lane_dict(self, lane_nrs: list) -> dict:
        return {lane_nr: lane_type for lane_nr, lane_type in self.road_info.obj_eigs.items()
                if lane_nr in lane_nrs and lane_type not in ["Puntstuk"]}

    def __combine_and_trim_geoms(self) -> LineString:
        for section in self.sections:
            measure_start = self.km[0]
            measure_end = self.km[1]
            section_start = section.pos_eigs.km[0]
            section_end = section.pos_eigs.km[1]
            distance_start_normalized = (measure_start - section_start) / (section_end - section_start)
            distance_end_normalized = (measure_end - section_start) / (section_end - section_start)
            point1 = line_interpolate_point(section.pos_eigs.geometrie, distance_start_normalized)
            point2 = line_interpolate_point(section.pos_eigs.geometrie, distance_end_normalized)

            return LineString([point1, point2])
        # TODO: Combine multiple trimmed geoms if necessary
        # return combined_trimmed_geom

    def __make_werkruimte(self):
        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkruimte = self.__get_lanes_werkruimte(self.road_info)

        # Initialise werkvak
        if lanes_werkruimte:
            Werkruimte(self, lanes_werkruimte)
        else:
            logger.info(f"Voor deze werkzaamheden worden geen tijdelijke verkeersmaatregelen voorgeschreven.")

    def __get_lanes_werkruimte(self, road_info: ObjectInfo) -> list:
        all_lane_nrs = list(sorted([lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items()
                                    if isinstance(lane_nr, int) and lane_type not in "Puntstuk"]))
        main_lane_nrs = [lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items() if isinstance(lane_nr, int)
                         and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging", "Weefstrook"]]

        lane_nrs_left = all_lane_nrs[:all_lane_nrs.index(main_lane_nrs[0])]
        lane_nrs_right = all_lane_nrs[all_lane_nrs.index(main_lane_nrs[-1])+1:]

        left_request_lane_nr = self.edge_left[0]
        right_request_lane_nr = self.edge_right[0]

        # Request is defined on two sides
        if left_request_lane_nr and right_request_lane_nr:
            keep_left_open = True  # If False: keep right side open.

            n_main_lanes_left = left_request_lane_nr - 1
            n_main_lanes_right = max(main_lane_nrs) - right_request_lane_nr

            if n_main_lanes_left < n_main_lanes_right:
                keep_left_open = False
            elif n_main_lanes_left > n_main_lanes_right:
                keep_left_open = True
            else:
                # Check if leftmost or rightmost lanes are lane types that are generally smaller.
                # Desired result: if vluchtstrook on both sides, then left side should be open.
                if road_info.obj_eigs[1] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = False
                if road_info.obj_eigs[self.n_lanes] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = True

            if keep_left_open:
                return self.__get_lane_dict(list(range(min(all_lane_nrs), self.n_lanes + 1)))  # Case TR3 or LR4
            else:
                return self.__get_lane_dict(list(range(1, max(all_lane_nrs) + 1)))  # Case TL2 or LL3

        # Request is only defined on one side
        over_24h = not self.under_24h
        left_request_space = self.edge_left[1]
        right_request_space = self.edge_right[1]

        condition_tl1 = self.under_24h and left_request_space and left_request_space <= 3.50

        condition_tr1 = (self.under_24h and right_request_space
                         and 1.10 < right_request_space <= self.sphere_of_influence)
        condition_tr2 = self.under_24h and right_request_space and right_request_space <= 1.10

        condition_ll1 = over_24h and left_request_space and left_request_space > 0.25
        condition_ll2 = over_24h and left_request_space and left_request_space <= 0.25

        condition_lr2 = over_24h and right_request_space and 1.50 < right_request_space <= 2.50
        condition_lr3 = over_24h and right_request_space and right_request_space <= 1.50

        if condition_tl1:
            return lane_nrs_left

        elif condition_tr1:
            return lane_nrs_right

        elif condition_tr2:
            return lane_nrs_right + [max(main_lane_nrs)]

        elif condition_ll1:
            return lane_nrs_left

        elif condition_ll2:
            return lane_nrs_left  # And lane narrowing

        elif condition_lr2:
            return lane_nrs_right  # And lane narrowing

        elif condition_lr3:
            return lane_nrs_right

        else:
            return {}


class Werkruimte(Oppervlak):
    def __init__(self, request: Aanvraag) -> None:
        self.request = request
        self.surf_type = WERKRUIMTE
        self.color = "orange"

        self.determine_edges()

        super().__init__(self)

        self.make_veiligheidsruimte()

    def make_veiligheidsruimte(self):
        # if self.bereik[0] < self.bereik[1]:
        #
        # else:
        Veiligheidsruimte(self.request)

    def determine_edges(self):
        return


class Veiligheidsruimte(Oppervlak):
    def __init__(self, request: Aanvraag) -> None:
        self.request = request
        self.surf_type = VEILIGHEIDSRUIMTE
        self.color = "yellow"
        
        super().__init__(self)
        
        self.make_werkruimte()

    def make_werkvak(self):
        # Find next upstream row compared to self.km_start
        next_upstream_km = 13.5
        # Find next downstream row compared to self.km_end
        next_downstream_km = 14.7

        Werkruimte(self.request)


class Werkvak(Oppervlak):
    def __init__(self, request: Aanvraag, lanes: dict) -> None:
        self.request = request
        self.lanes = lanes
        self.surf_type = WERKVAK
        self.color = "cyan"

        super().__init__(self)


