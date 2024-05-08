from road_model import WegModel, ObjectInfo
from utils import *
from shapely import *
logger = logging.getLogger(__name__)

AANVRAAG = 200
WERKRUIMTE = 201
VEILIGHEIDSRUIMTE = 202
WERKVAK = 203

AFZETTING_BAKENS = 300
AFZETTING_BARRIER_LAGER_DAN_80CM = 301
AFZETTING_BARRIER_HOGER_DAN_80CM = 302

TL1 = 400
TL2 = 401
TR1 = 402
TR2 = 403
TR3 = 404
LL1 = 405
LL2 = 406
LL3 = 407
LR1 = 408
LR2 = 409
LR3 = 410


class Rand:
    def __init__(self, rijstrook: int | None, afstand: float):
        self.lane = rijstrook
        self.distance = afstand

    def __repr__(self) -> str:
        if self.lane:
            if self.distance >= 0:
                return f"Rijstrook {self.lane} +{self.distance}"
            else:
                return f"Rijstrook {self.lane} {self.distance}"
        else:
            if self.distance >= 0:
                return f"+{self.distance}"
            else:
                return f"{self.distance}"


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

    __BREEDTE_BARRIER = 0.60  # Estimate, in meters
    __BREEDTE_BAKENS = 0.40  # Estimate, in meters

    __TUSSENRUIMTE = {
        AFZETTING_BAKENS: {WERKVAK: 0.5 * __BREEDTE_BAKENS + 0.60, VEILIGHEIDSRUIMTE: 0.60},
        AFZETTING_BARRIER_LAGER_DAN_80CM: {WERKVAK: 0.5 * __BREEDTE_BARRIER + 0.60, VEILIGHEIDSRUIMTE: 0.60},
        AFZETTING_BARRIER_HOGER_DAN_80CM: {WERKVAK: 0.5 * __BREEDTE_BARRIER + 0.0, VEILIGHEIDSRUIMTE: 0.0},
    }

    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str,
                 randen: dict[str: Rand] | None,
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:
        assert 0 < len(randen) <= 2, "Specificeer één of twee randen."

        self.roadmodel = wegmodel
        self.roadside = wegkant
        self.km = [km_start, km_end]
        self.hectoletter = hectoletter

        self.edges = randen

        self.max_v = maximumsnelheid
        self.under_24h = korter_dan_24h
        self.demarcation = afzetting

        self.surface_type = AANVRAAG

        self.sections = self.roadmodel.get_section_info_by_bps(km=self.km, side=self.roadside, hecto=self.hectoletter)
        if not self.sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.km} {self.roadside} {self.hectoletter}")

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_info = self.sections[0]
        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        self.werkruimte = Werkruimte(self)
        self.veiligheidsruimte = Veiligheidsruimte(self)
        self.werkvak = Werkvak(self)

        self.step_1_determine_minimal_werkruimte()
        # self.step_2_determine_area_sizes()
        # self.step_3_determine_legend_request()
        # self.step_4_solve_legend_request()
        # self.step_5_adjust_area_sizes()

        self.report_request()

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

        # Determine minimal length in regard to the MSIs
        self.werkvak.adjust_length_to_msis()
        self.veiligheidsruimte.adjust_length_to_werkvak()
        self.werkruimte.adjust_length_to_veiligheidsruimte()

    def step_3_determine_legend_request(self):
        return  # TODO

    def step_4_solve_legend_request(self):
        return  # TODO

    def step_5_adjust_area_sizes(self):
        return  # TODO

    def report_request(self):
        logger.info(f"Aanvraag aangemaakt met randen: {self.edges}")
        logger.info(f"Werkruimte aangemaakt met randen: {self.werkruimte.edges}")
        # logger.info(f"Veiligheidsruimte aangemaakt met randen: {self.veiligheidsruimte.edges}")
        # logger.info(f"Werkvak aangemaakt met randen: {self.werkvak.edges}")


class Werkruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKRUIMTE
        self.request = request
        self.edges = deepcopy(request.edges)  # RIGHT HERE
        self.km = request.km

    def determine_minimal_werkruimte_size(self):
        lanes = self.request.road_info.obj_eigs
        all_lane_nrs = [lane_nr for lane_nr, lane_type in lanes.items() if isinstance(lane_nr, int) and
                        lane_type not in ["Puntstuk"]]
        main_lane_nrs = [lane_nr for lane_nr, lane_type in lanes.items() if isinstance(lane_nr, int) and
                         lane_type in ["Rijstrook", "Splitsing", "Samenvoeging", "Weefstrook"]]
        first_lane_nr = min(all_lane_nrs)
        last_lane_nr = max(all_lane_nrs)

        # In case the request is defined in terms of two edges...
        if self.request.edges['L'] and self.request.edges['R']:
            # Sanity checks for request in this case.
            assert self.request.edges['L'].lane is None or self.request.edges['L'].lane in main_lane_nrs, \
                "Opgegeven rijstrooknummer voor rand links behoort niet tot de hoofdstroken."
            assert self.request.edges['R'].lane is None or self.request.edges['R'].lane in main_lane_nrs, \
                "Opgegeven rijstrooknummer voor rand rechts behoort niet tot de hoofdstroken."
            assert self.request.edges['L'].distance is None or self.request.edges['L'].distance >= 0, \
                "Geef een positieve afstand voor de linkerrand op."
            assert self.request.edges['R'].distance is None or self.request.edges['R'].distance <= 0, \
                "Geef een negatieve afstand voor de rechterrand op."

            # Determine if expansion is necessary
            if (first_lane_nr in [(self.request.edges['L'].lane), (self.request.edges['R'].lane)]
                    or last_lane_nr in [(self.request.edges['L'].lane), (self.request.edges['R'].lane)]):
                # The request goes all the way up to a side of the road. Expansion does not need to be determined.
                logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid.")
                return

            # In case the request is defined in lanes on one side...
            # if self.request.edges['L'] or self.request.edges['R']:
            #     logger.warning("Deze situatie is nog niet uitgewerkt. De werkruimte wordt even groot als de aanvraag.")
            #     return

            keep_left_open = True  # If False: keep right side open.

            n_main_lanes_left = self.request.edges['L'].lane - min(main_lane_nrs)
            n_main_lanes_right = max(main_lane_nrs) - self.request.edges['R'].lane

            if n_main_lanes_left < n_main_lanes_right:
                keep_left_open = False
            elif n_main_lanes_left > n_main_lanes_right:
                keep_left_open = True
            else:
                # Check if leftmost or rightmost lanes are lane types that are generally smaller.
                # Desired result: if vluchtstrook on both sides, then left side should be open.
                if lanes[1] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = False
                if lanes[self.request.n_lanes] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = True

            if keep_left_open:
                # Adjust to far right side of road. Case TR3 or LR3
                self.edges['R'] = Rand(rijstrook=last_lane_nr, afstand=0.0)
            else:
                # Adjust to far left side of road. Case TL2 or LL3
                self.edges['L'] = Rand(rijstrook=first_lane_nr, afstand=0.0)
            return

        # In case the request is defined in terms of one edge.
        category = self.determine_request_category()
        logger.info(f"Deze situatie valt onder categorienummer {category}.")

        if category == TL1:
            self.edges['R'] = Rand(rijstrook=min(main_lane_nrs), afstand=-0.91)
        elif category == LL1:
            self.edges['R'] = Rand(rijstrook=None, afstand=-0.91)
        elif category == LL2:
            self.edges['R'] = Rand(rijstrook=None, afstand=-0.91)
            # And lane narrowing.
        elif category == TR1:
            self.edges['L'] = Rand(rijstrook=None, afstand=+0.91)
        elif category == TR2:
            self.edges['L'] = Rand(rijstrook=max(main_lane_nrs), afstand=+0.91)
        elif category == LR1:
            self.edges['L'] = Rand(rijstrook=None, afstand=+0.91)
        elif category == LR2:
            self.edges['L'] = Rand(rijstrook=max(main_lane_nrs), afstand=+1.0)
            # And lane narrowing.
        else:
            logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid (geen effect op weg).")

    def determine_request_category(self) -> int:
        left_space = self.edges['L'].distance if self.edges['L'] else None
        right_space = self.edges['R'].distance if self.edges['R'] else None
        assert left_space or right_space, "Specificeer hoeveelheid overgebleven ruimte in de aanvraag."

        if self.request.under_24h and left_space and left_space >= -3.50:
            return TL1
        elif self.request.under_24h and right_space and 1.10 < right_space <= self.request.sphere_of_influence:
            return TR1
        elif self.request.under_24h and right_space and 0.0 <= right_space <= 1.10:
            return TR2
        elif not self.request.under_24h and left_space and left_space < -0.25:
            return LL1
        elif not self.request.under_24h and left_space and 0.0 >= left_space >= -0.25:
            return LL2
        elif not self.request.under_24h and right_space and 1.50 < right_space <= 2.50:
            return LR1
        elif not self.request.under_24h and right_space and 0.0 <= right_space <= 1.50:
            return LR2
        else:
            logger.warning("Geen passende categorie gevonden voor de gegeven aanvraag.")
            return 0

    def adjust_edges_to_veiligheidsruimte(self):
        return  # TODO

    def adjust_length_to_veiligheidsruimte(self):
        return  # TODO


class Veiligheidsruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = VEILIGHEIDSRUIMTE
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_werkruimte(self):
        return  # TODO

    def adjust_edges_to_werkvak(self):
        return  # TODO

    def adjust_length_to_werkvak(self):
        return  # TODO


class Werkvak:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKVAK
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_veiligheidsruimte(self):
        return  # TODO

    def adjust_edges_to_road(self):
        return  # TODO

    def adjust_length_to_msis(self):
        return  # TODO

