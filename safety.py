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

    __WIDTH_OFFSET = {
        AFZETTING_BAKENS: {VEILIGHEIDSRUIMTE: __BREEDTE_BAKENS / 2, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_LAGER_DAN_80CM: {VEILIGHEIDSRUIMTE: __BREEDTE_BARRIER / 2, WERKRUIMTE: 0.60},
        AFZETTING_BARRIER_HOGER_DAN_80CM: {VEILIGHEIDSRUIMTE: __BREEDTE_BARRIER / 2, WERKRUIMTE: 0},
    }

    __SURFACE_NAMES = {
        AANVRAAG: "Aanvraag",
        WERKVAK: "Werkvak",
        VEILIGHEIDSRUIMTE: "Veiligheidsruimte",
        WERKRUIMTE: "Werkruimte",
    }

    def __init__(self, parent) -> None:
        self.parent = parent

        self.width_offset = self.__WIDTH_OFFSET.get(self.parent.afzetting, None).get(self.parent.surf_type, 0)
        self.width = self.__get_width()

        self.log_surface()

    def __get_width(self) -> list:
        left_edge_meter = (self.parent.edge_left[0] - 1) * 3.5 + self.parent.edge_left[1]
        right_edge_meter = (self.parent.edge_right[0]) * 3.5 + self.parent.edge_right[1]
        return [left_edge_meter, right_edge_meter]

    def log_surface(self):
        logger.info(f"Oppervlak '{self.__SURFACE_NAMES.get(self.parent.surf_type, 'ONBEKEND')}' gemaakt "
                    f"aan kant {self.parent.wegkant}, "
                    f"van {self.parent.bereik[0]} tot {self.parent.bereik[1]}, "
                    f"met breedte {self.parent.width}.")


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
                 rand_links: tuple = None, rand_rechts: tuple = None,
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:

        assert rand_links or rand_rechts, "Specificeer minstens één eis."

        self.surf_type = AANVRAAG

        self.wegmodel = wegmodel
        self.wegkant = wegkant
        self.bereik = [km_start, km_end]
        self.hectoletter = hectoletter

        self.edge_left = rand_links
        self.edge_right = rand_rechts

        self.max_v = maximumsnelheid
        self.korter_dan_24h = korter_dan_24h
        self.afzetting = afzetting

        self.color = "brown"

        self.sections = self.wegmodel.get_section_info_by_bps(km=self.bereik, side=self.wegkant, hecto=self.hectoletter)
        if not self.sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.bereik} {self.wegkant} {self.hectoletter}")

        self.geometry = self.__combine_and_trim_geoms()

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_info = self.sections[0]
        self.all_lanes = list(sorted([lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items()
                                      if isinstance(lane_nr, int) and lane_type not in "Puntstuk"]))
        self.main_lanes = [lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items() if isinstance(lane_nr, int)
                           and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging", "Weefstrook"]]

        self.lane_nrs_left = self.all_lanes[:self.all_lanes.index(self.main_lanes[0])]
        self.lanes_left = self.__get_lane_dict(self.lane_nrs_left)
        self.lane_nrs_right = self.all_lanes[self.all_lanes.index(self.main_lanes[-1])+1:]
        self.lanes_right = self.__get_lane_dict(self.lane_nrs_right)

        self.lane_nrs_right_for_tr2 = self.all_lanes[self.all_lanes.index(self.main_lanes[-1]):]
        self.lanes_right_for_tr2 = self.__get_lane_dict(self.lane_nrs_right)

        super().__init__(self)

        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        self.__make_werkvak()

    def __get_lane_dict(self, lane_nrs: list) -> dict:
        return {lane_nr: lane_type for lane_nr, lane_type in self.road_info.obj_eigs.items()
                if lane_nr in lane_nrs and lane_type not in ["Puntstuk"]}

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

    def __make_werkvak(self):
        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = self.__get_lanes_werkvak(self.road_info)

        # Initialise werkvak
        if lanes_werkvak:
            Werkvak(self.wegkant, self.bereik, self.afzetting, lanes_werkvak)
        else:
            logger.info(f"Voor deze werkzaamheden worden geen tijdelijke verkeersmaatregelen voorgeschreven.")

    def __get_lanes_werkvak(self, road_info: ObjectInfo) -> dict:
        if self.stroken:
            keep_left_open = True  # If False: keep right side open.

            n_main_lanes_left = min(self.stroken) - 1
            n_main_lanes_right = self.n_lanes - max(self.stroken)
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
                return self.__get_lane_dict(list(range(min(self.stroken), self.n_lanes + 1)))  # Case TR3 or LR4
            else:
                return self.__get_lane_dict(list(range(1, max(self.stroken) + 1)))  # Case TL2 or LL3

        langer_dan_24h = not self.korter_dan_24h

        condition_tl1 = self.korter_dan_24h and self.ruimte_links and self.ruimte_links <= 3.50

        condition_tr1 = (self.korter_dan_24h and self.ruimte_rechts
                         and 1.10 < self.ruimte_rechts <= self.sphere_of_influence)
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
            return self.lanes_right_for_tr2

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


class Werkvak(Oppervlak):
    def __init__(self, aanvraag: Aanvraag) -> None:
        self.aanvraag = aanvraag
        self.surf_type = WERKVAK
        self.color = "cyan"
        
        super().__init__(self)
        
        self.make_veiligheidsruimte()

    def make_veiligheidsruimte(self):
        # if self.bereik[0] < self.bereik[1]:
        #
        # else:
        Veiligheidsruimte(self.aanvraag)


class Veiligheidsruimte(Oppervlak):
    def __init__(self, aanvraag: Aanvraag) -> None:
        self.aanvraag = aanvraag
        self.surf_type = VEILIGHEIDSRUIMTE
        self.color = "yellow"
        
        super().__init__(self)
        
        self.make_werkruimte()

    def make_werkruimte(self):
        # Find next upstream row compared to self.km_start
        next_upstream_km = 13.5
        # Find next downstream row compared to self.km_end
        next_downstream_km = 14.7

        Werkruimte(self.aanvraag)


class Werkruimte(Oppervlak):
    def __init__(self, aanvraag: Aanvraag) -> None:
        self.aanvraag = aanvraag
        self.surf_type = AANVRAAG
        self.color = "orange"

        super().__init__(self)

