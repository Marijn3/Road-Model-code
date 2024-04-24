from road_model import WegModel, ObjectInfo
from utils import *
from shapely import *
logger = logging.getLogger(__name__)

AANVRAAG = 200
WERKVAK = 201
VEILIGHEIDSRUIMTE = 202
WERKRUIMTE = 203

AFZETTING_BAKENS = 300
AFZETTING_BARRIER_LAGER_DAN_80CM = 301
AFZETTING_BARRIER_HOGER_DAN_80CM = 302


class Oppervlak:

    __BREEDTE_BARRIER = 0.40  # Schatting
    __BREEDTE_BAKENS = 0.20  # Schatting

    __WIDTHS = {
        AFZETTING_BAKENS: {VEILIGHEIDSRUIMTE: __BREEDTE_BAKENS / 2, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_LAGER_DAN_80CM: {VEILIGHEIDSRUIMTE: __BREEDTE_BARRIER / 2, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_HOGER_DAN_80CM: {VEILIGHEIDSRUIMTE: __BREEDTE_BARRIER / 2, WERKRUIMTE: 0},
    }

    def __init__(self, roadside: str, km_start: float, km_end: float,
                 surf_type: int, unfiltered_lanes: dict, afzetting: int) -> None:
        self.roadside = roadside
        self.km_start = km_start
        self.km_end = km_end
        self.surf_type = surf_type
        self.afzetting = afzetting
        self.lanes = {lane_nr: lane_type for lane_nr, lane_type in unfiltered_lanes.items() if isinstance(lane_nr, int)}

        self.width_safety_distances = self.__WIDTHS.get(self.afzetting, None)
        self.width_offset = self.width_safety_distances.get(self.surf_type, 0)

        self.width = self.get_width()

        self.log_surface()

    def log_surface(self):
        logger.info(f"Oppervlak '{self.surf_type}' gemaakt aan kant {self.roadside}, "
                    f"van {self.km_start} tot {self.km_end}, met stroken {self.lanes} en breedte {self.width}.")

    def get_width(self) -> list:
        lane_numbers = self.lanes.keys()
        min_width = min((lane - 1) * 3.5 for lane in lane_numbers)
        max_width = max(lane * 3.5 - self.width_offset for lane in lane_numbers)
        return [min_width, max_width]


class Werkvak(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: dict, afzetting) -> None:
        super().__init__(roadside, km_start, km_end, WERKVAK, lanes, afzetting)
        self.color = "cyan"
        self.make_veiligheidsruimte(afzetting)

    def make_veiligheidsruimte(self, afzetting):
        if self.km_start < self.km_end:
            Veiligheidsruimte(self.roadside, self.km_start-0.1, self.km_end+0.1, self.lanes, afzetting)
        else:
            Veiligheidsruimte(self.roadside, self.km_start+0.1, self.km_end-0.1, self.lanes, afzetting)


class Veiligheidsruimte(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: dict, afzetting: int) -> None:
        super().__init__(roadside, km_start, km_end, VEILIGHEIDSRUIMTE, lanes, afzetting)
        self.color = "yellow"
        self.make_werkruimte(afzetting)

    def make_werkruimte(self, afzetting):
        # Find next upstream row compared to self.km_start
        next_upstream_km = 13.5
        # Find next downstream row compared to self.km_end
        next_downstream_km = 14.7

        Werkruimte(self.roadside, next_upstream_km, next_downstream_km, self.lanes, afzetting)

class Werkruimte(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: dict, afzetting: int) -> None:
        super().__init__(roadside, km_start, km_end, WERKRUIMTE, lanes, afzetting)
        self.color = "orange"


class Aanvraag(Oppervlak):

    # Source: WIU 2020 - Werken op autosnelwegen 03-10-2023 Rijkswaterstaat
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
                 ruimte_links: float = None, ruimte_midden: list = None, ruimte_rechts: float = None,
                 max_v: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:
        if not sum(1 for v in [ruimte_links, ruimte_midden, ruimte_rechts] if v is not None) == 1:
            raise InterruptedError("Specificeer één eis.")
        assert not ruimte_links or (ruimte_links and ruimte_links > 0),\
            "Onjuiste aanvraag. Definieer positieve afstanden."
        assert not ruimte_rechts or (ruimte_rechts and ruimte_rechts > 0),\
            "Onjuiste aanvraag. Definieer positieve afstanden."

        self.wegmodel = wegmodel
        self.hectoletter = hectoletter
        self.ruimte_links = ruimte_links
        self.ruimte_midden = ruimte_midden
        self.ruimte_rechts = ruimte_rechts
        self.max_v = max_v
        self.korter_dan_24h = korter_dan_24h
        self.afzetting = afzetting
        self.bereik = [km_start, km_end]
        self.wegkant = wegkant
        self.color = "brown"

        self.sections = self.__get_road_info()

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_info = self.sections[0]

        self.geometry = self.__combine_and_trim_geoms()

        self.all_lanes = list(sorted([lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items() if isinstance(lane_nr, int) and lane_type not in "Puntstuk"]))
        self.main_lanes = [lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items()
                           if isinstance(lane_nr, int) and lane_type in self.wegmodel.MAIN_LANE_TYPES]

        self.lane_nrs_left = self.all_lanes[:self.all_lanes.index(self.main_lanes[0])]
        self.lanes_left = self.__get_lane_dict(self.lane_nrs_left)
        self.lane_nrs_right = self.all_lanes[self.all_lanes.index(self.main_lanes[-1])+1:]
        self.lanes_right = self.__get_lane_dict(self.lane_nrs_right)

        # if self.ruimte_links and not self.lane_nrs_left: ...

        self.lane_nrs_right_tr2 = self.all_lanes[self.all_lanes.index(self.main_lanes[-1]):]
        self.lanes_right_tr2 = self.__get_lane_dict(self.lane_nrs_right)

        self.request_lanes = self.__determine_request_lanes()

        super().__init__(wegkant, km_start, km_end, AANVRAAG, self.request_lanes, self.afzetting)

        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        self.__make_werkvak()

    def __get_lane_dict(self, lane_nrs: list) -> dict:
        return {lane_nr: lane_type for lane_nr, lane_type in self.road_info.obj_eigs.items()
                if lane_nr in lane_nrs and lane_type not in ["Puntstuk"]}

    def __get_road_info(self) -> list:
        """Obtain surrounding geometry and road properties."""
        sections = self.wegmodel.get_section_info_by_bps(km=self.bereik, side=self.wegkant, hecto=self.hectoletter)

        if not sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.bereik} {self.wegkant} {self.hectoletter}")

        return sections

    def __combine_and_trim_geoms(self) -> LineString:
        for section in self.sections:
            measure_start = self.bereik[0]
            measure_end = self.bereik[1]
            section_start = section.pos_eigs.km[0]
            section_end = section.pos_eigs.km[1]
            distance_start_normalized = (measure_start - section_start) / (section_end - section_start)
            distance_end_normalized = (measure_end - section_start) / (section_end - section_start)
            point1 = line_interpolate_point(section.pos_eigs.geometrie, distance_start_normalized)
            point2 = line_interpolate_point(section.pos_eigs.geometrie, distance_end_normalized)

            return LineString([point1, point2])
        # TODO: Combine multiple trimmed geoms if necessary
        # return combined_trimmed_geom

    def __determine_request_lanes(self) -> dict:
        if self.ruimte_links:
            return self.lanes_left
        if self.ruimte_midden:
            assert all(lane_nr in self.main_lanes for lane_nr in self.ruimte_midden), \
                "Een aangevraagde rijstrook hoort niet bij de hoofdstroken."
            return self.__get_lane_dict(self.ruimte_midden)
        if self.ruimte_rechts:
            return self.lanes_right

    def __make_werkvak(self):
        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = self.__get_lanes_werkvak(self.road_info)

        # Initialise werkvak
        if lanes_werkvak:
            Werkvak(self.roadside, self.km_start, self.km_end, lanes_werkvak, self.afzetting)
        else:
            logger.info(f"Voor deze werkzaamheden worden geen tijdelijke verkeersmaatregelen voorgeschreven.")

    def __get_lanes_werkvak(self, road_info: ObjectInfo) -> dict:
        if self.ruimte_midden:
            keep_left_open = True  # If False: keep right side open.

            n_main_lanes_left = min(self.ruimte_midden) - 1
            n_main_lanes_right = self.n_lanes - max(self.ruimte_midden)
            if n_main_lanes_left < n_main_lanes_right:
                keep_left_open = False
            elif n_main_lanes_left == n_main_lanes_right:
                if road_info.obj_eigs[1] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = False
                if road_info.obj_eigs[self.n_lanes] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = True
                # Desired result: if vluchtstrook on both sides and space equal, then left side should be open.
            else:
                keep_left_open = True

            if keep_left_open:
                return self.__get_lane_dict(list(range(min(self.ruimte_midden), self.n_lanes + 1)))  # Case TR3 or LR4
            else:
                return self.__get_lane_dict(list(range(1, max(self.ruimte_midden) + 1)))  # Case TL2 or LL3

        langer_dan_24h = not self.korter_dan_24h

        condition_tl1 = self.korter_dan_24h and self.ruimte_links and self.ruimte_links <= 3.50

        condition_tr1 = self.korter_dan_24h and self.ruimte_rechts and 1.10 < self.ruimte_rechts <= self.sphere_of_influence
        condition_tr2 = self.korter_dan_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.10

        condition_ll1 = langer_dan_24h and self.ruimte_links and self.ruimte_links > 0.25
        condition_ll2 = langer_dan_24h and self.ruimte_links and self.ruimte_links <= 0.25

        condition_lr2 = langer_dan_24h and self.ruimte_rechts and 1.50 < self.ruimte_rechts <= 2.50
        condition_lr3 = langer_dan_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.50

        if condition_tl1:
            return self.lanes_left

        elif condition_tr1:
            return self.lanes_right

        elif condition_tr2:
            return self.lanes_right_tr2

        elif condition_ll1:
            return self.lanes_left

        elif condition_ll2:
            return self.lanes_left  # And lane narrowing

        elif condition_lr2:
            return self.lanes_right

        elif condition_lr3:
            return self.lanes_right  # And lane narrowing

        else:
            return {}
