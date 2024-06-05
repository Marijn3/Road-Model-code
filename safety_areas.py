from road_model import WegModel
from utils import *

logger = logging.getLogger(__name__)

AANVRAAG = 200
WERKRUIMTE = 201
VEILIGHEIDSRUIMTE = 202
WERKVAK = 203

BREEDTE_BARRIER = 0.40  # Estimate, in meters
BREEDTE_GELEIDEBAKENS = 0.25  # Based on WIU 2020 – Werken op autosnelwegen [p117], in meters


class AFZETTINGEN:
    BAKENS = 300
    BARRIER_ONDER_80CM = 301
    BARRIER_BOVEN_80CM = 302


TUSSENRUIMTE = {
    AFZETTINGEN.BAKENS: {WERKVAK: 0.5 * BREEDTE_GELEIDEBAKENS, VEILIGHEIDSRUIMTE: 0.60},
    AFZETTINGEN.BARRIER_ONDER_80CM: {WERKVAK: 0.5 * BREEDTE_BARRIER, VEILIGHEIDSRUIMTE: 0.60},
    AFZETTINGEN.BARRIER_BOVEN_80CM: {WERKVAK: 0.5 * BREEDTE_BARRIER, VEILIGHEIDSRUIMTE: 0.0},
}


class Rand:
    def __init__(self, rijstrook: int | None, afstand: float):
        self.lane = rijstrook
        self.distance = afstand

    def __repr__(self) -> str:
        position = f"Rijstrook {self.lane}" if self.lane else f"Naast weg"
        if self.distance > 0:
            return f"{position} +{self.distance}m"
        else:
            return f"{position} {self.distance}m"

    def move_edge(self, move_distance, side):
        # TODO: Make exceptions for lane narrowing
        if side == "L":
            direction_modifier = -1
        else:
            direction_modifier = 1

        if self.distance < -move_distance * direction_modifier:  # The edge will cross 0
            self.lane = self.lane + 1 * direction_modifier if self.lane else None
        self.distance = round(self.distance + move_distance * direction_modifier, 2)


class Aanvraag:

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

    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str,
                 randen: dict[str: Rand],
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTINGEN.BAKENS) -> None:
        self.roadmodel = wegmodel
        self.roadside = wegkant
        self.km = [km_start, km_end]
        self.hecto_character = hectoletter
        self.edges = randen
        self.max_v = maximumsnelheid
        self.under_24h = korter_dan_24h
        self.demarcation = afzetting

        self.run_sanity_checks()

        logger.info(f"Aanvraag met kmrange={km_start}, {km_end} randen={randen}, korter dan 24h={korter_dan_24h}.")

        self.surface_type = AANVRAAG
        self.requires_lane_narrowing = False
        self.open_side = None

        self.sections = self.roadmodel.get_section_info_by_bps(self.km, self.roadside, self.hecto_character)
        if not self.sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.km} {self.roadside} {self.hecto_character}")

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_info = self.sections[0]
        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        self.lanes = self.road_info.obj_eigs
        self.all_lane_nrs = [lane_nr for lane_nr, lane_type in self.lanes.items() if isinstance(lane_nr, int) and
                             lane_type not in ["Puntstuk"]]
        self.main_lane_nrs = [lane_nr for lane_nr, lane_type in self.lanes.items() if isinstance(lane_nr, int) and
                              lane_type not in ["Puntstuk", "Vluchtstrook", "Spitsstrook", "Plusstrook"]]
        self.first_lane_nr = min(self.all_lane_nrs)
        self.last_lane_nr = max(self.all_lane_nrs)

        self.werkruimte = Werkruimte(self)
        self.veiligheidsruimte = Veiligheidsruimte(self)
        self.werkvak = Werkvak(self)

        self.step_1_determine_minimal_werkruimte()
        self.step_2_determine_area_sizes()
        # self.step_3_determine_legend_request()
        # self.step_4_solve_legend_request()
        # self.step_5_adjust_area_sizes()

        self.report_request()

    def run_sanity_checks(self):
        assert len(self.edges) == 2, \
            "Specificeer beide randen."
        assert self.edges['L'].distance and self.edges['R'].distance, \
            "Specificeer afstand vanaf belijning in de aanvraag."
        assert abs(self.edges["L"].distance) != abs(self.edges["R"].distance), \
            "Specificeer ongelijke afstanden."

    def step_1_determine_minimal_werkruimte(self):
        self.werkruimte.determine_minimal_werkruimte_size()

    def step_2_determine_area_sizes(self):
        # Determine minimal width from the original area
        self.veiligheidsruimte.adjust_edges_to_werkruimte()
        self.werkvak.adjust_edges_to_veiligheidsruimte()

        # Determine convenient width in regard to the road
        self.werkvak.adjust_edges_to_road()
        self.veiligheidsruimte.adjust_edges_to_werkvak()
        self.werkruimte.adjust_edges_to_veiligheidsruimte()

        # Determine minimal length wtih respect to the MSIs  # TODO
        # self.werkvak.adjust_length_to_msis()
        # self.veiligheidsruimte.adjust_length_to_werkvak()
        # self.werkruimte.adjust_length_to_veiligheidsruimte()

    def step_3_determine_legend_request(self):
        return  # TODO

    def step_4_solve_legend_request(self):
        return  # TODO

    def step_5_adjust_area_sizes(self):
        return  # TODO

    def report_request(self):
        logger.info(f"Aanvraag aangemaakt met randen: {self.edges}")
        logger.info(f"Werkruimte aangemaakt met randen: {self.werkruimte.edges}")
        logger.info(f"Veiligheidsruimte aangemaakt met randen: {self.veiligheidsruimte.edges}")
        logger.info(f"Werkvak aangemaakt met randen: {self.werkvak.edges}")


class Werkruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKRUIMTE
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km
        self.category = str()

    def determine_minimal_werkruimte_size(self):
        if self.request.edges["L"].lane and self.request.edges["R"].lane:
            self.determine_request_category_onroad()
        elif self.request.edges["L"].lane or self.request.edges["R"].lane:
            # TODO: Uitwerken wat er in deze situatie moet gebeuren.
            logger.warning("Deze situatie is nog niet uitgewerkt. De werkruimte wordt even groot als de aanvraag.")
            return
        else:
            self.determine_request_category_roadside()

        self.apply_category_measures()

    def apply_category_measures(self):
        if not self.category:
            logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid (geen effect op de weg).")
        else:
            logger.info(f"Deze situatie valt onder categorie {self.category}.")

        if self.category == "A":
            self.make_edge(side_to_adjust=self.request.open_side, lane=None, distance_r=-0.81)
        elif self.category == "B":
            self.make_edge(side_to_adjust=self.request.open_side, lane=min(self.request.main_lane_nrs), distance_r=-0.81)
        elif self.category == "C":
            self.request.requires_lane_narrowing = True
            self.make_edge(side_to_adjust=self.request.open_side, lane=None, distance_r=-0.0)
        elif self.category == "D":
            other_side = "R" if self.request.open_side == "L" else "L"
            self.make_edge(side_to_adjust=other_side, lane=None, distance_r=+5.0)

    def make_edge(self, side_to_adjust: str, lane: int | None, distance_r: float) -> None:
        if side_to_adjust == "L":
            distance_r = -distance_r
        self.edges[side_to_adjust] = Rand(rijstrook=lane, afstand=+distance_r)

    def determine_request_category_onroad(self) -> None:
        self.do_onroad_sanity_checks()
        self.category = "D"

        # Determine if expansion is not necessary. When the request goes all the way up
        # to a side of the road, expansion of the request does not need to be determined.
        if (self.request.first_lane_nr in [self.request.edges['L'].lane, self.request.edges['R'].lane]
                or self.request.last_lane_nr in [self.request.edges['L'].lane, self.request.edges['R'].lane]):
            logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid.")
            return

        self.request.open_side = self.determine_open_side()

    def do_onroad_sanity_checks(self):
        assert self.request.edges['L'].lane is None or self.request.edges['L'].lane in self.request.main_lane_nrs, \
            "Opgegeven rijstrooknummer voor rand links behoort niet tot de hoofdstroken."
        assert self.request.edges['R'].lane is None or self.request.edges['R'].lane in self.request.main_lane_nrs, \
            "Opgegeven rijstrooknummer voor rand rechts behoort niet tot de hoofdstroken."
        assert self.request.edges['L'].distance is None or self.request.edges['L'].distance >= 0, \
            "Geef een positieve afstand voor de linkerrand op."
        assert self.request.edges['R'].distance is None or self.request.edges['R'].distance <= 0, \
            "Geef een negatieve afstand voor de rechterrand op."

    def determine_open_side(self) -> str:
        n_main_lanes_left = self.request.edges["L"].lane - min(self.request.main_lane_nrs)
        n_main_lanes_right = max(self.request.main_lane_nrs) - self.request.edges["R"].lane

        if n_main_lanes_left < n_main_lanes_right:
            return "R"
        elif n_main_lanes_left > n_main_lanes_right:
            return "L"
        else:
            open_side = "L"
            # Check if leftmost or rightmost lanes are lane types that are generally smaller.
            # Desired result: if vluchtstrook on both sides, then left side should be open.
            if self.request.lanes[1] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                open_side = "R"
            if self.request.lanes[self.request.n_lanes] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                open_side = "L"
            return open_side

    def determine_request_category_roadside(self):
        if abs(self.edges["L"].distance) < abs(self.edges["R"].distance):
            crit_dist = self.edges["L"].distance  # Space closest to road
        else:
            crit_dist = self.edges["R"].distance

        if self.edges["L"].distance >= 0 and self.edges["R"].distance >= 0:
            side_of_road = "R"
            self.request.open_side = "L"
        elif self.edges["L"].distance <= 0 and self.edges["R"].distance <= 0:
            side_of_road = "L"
            self.request.open_side = "R"
        else:
            raise Exception("Deze combinatie van randen is niet toegestaan.")

        variable_edge = 1.50  # defined as 0.25-1.50 [m]

        if ((self.request.under_24h and side_of_road == "R" and 1.10 < crit_dist <= self.request.sphere_of_influence)
                or (not self.request.under_24h and side_of_road == "L" and crit_dist < -0.25)
                or (not self.request.under_24h and side_of_road == "R" and variable_edge < crit_dist <= 2.50)):
            self.category = "A"

        elif ((self.request.under_24h and side_of_road == "L" and -3.50 <= crit_dist)
                or (self.request.under_24h and side_of_road == "R" and 0.0 <= crit_dist <= 1.10)):
            self.category = "B"

        elif ((not self.request.under_24h and side_of_road == "L" and -0.25 <= crit_dist <= 0.0)
                or (not self.request.under_24h and side_of_road == "R" and 0.0 <= crit_dist <= variable_edge)):
            self.category = "C"

        else:
            logger.info("Geen passende categorie gevonden voor de gegeven aanvraag.")

    def adjust_edges_to_veiligheidsruimte(self):
        self.edges = deepcopy(self.request.veiligheidsruimte.edges)
        side = self.request.open_side
        move_distance = -TUSSENRUIMTE[self.request.demarcation][VEILIGHEIDSRUIMTE]
        self.edges[side].move_edge(move_distance, side)
        return

    def adjust_length_to_veiligheidsruimte(self):
        return  # TODO


class Veiligheidsruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = VEILIGHEIDSRUIMTE
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_werkruimte(self) -> None:
        self.edges = deepcopy(self.request.werkruimte.edges)
        side = self.request.open_side
        move_distance = TUSSENRUIMTE[self.request.demarcation][self.surface_type]
        self.edges[side].move_edge(move_distance, side)
        return

    def adjust_edges_to_werkvak(self):
        self.edges = deepcopy(self.request.werkvak.edges)
        side = self.request.open_side
        move_distance = -TUSSENRUIMTE[self.request.demarcation][WERKVAK]
        self.edges[side].move_edge(move_distance, side)
        return

    def adjust_length_to_werkvak(self):
        return  # TODO


class Werkvak:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKVAK
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_veiligheidsruimte(self):
        self.edges = deepcopy(self.request.veiligheidsruimte.edges)
        side = self.request.open_side
        move_distance = TUSSENRUIMTE[self.request.demarcation][self.surface_type]
        self.edges[side].move_edge(move_distance, side)
        return

    def adjust_edges_to_road(self):
        if self.request.open_side == "L":
            self.edges["L"].distance = +0.0
        if self.request.open_side == "R":
            self.edges["R"].distance = -0.0
        return

    def adjust_length_to_msis(self):
        return  # TODO
