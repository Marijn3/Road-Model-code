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

    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 rand_links: tuple = None, rand_rechts: tuple = None,
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:
        assert rand_links or rand_rechts, "Specificeer minstens één rand."

        self.roadmodel = wegmodel
        self.roadside = wegkant
        self.km = [km_start, km_end]
        self.hectoletter = hectoletter

        self.edge_left = rand_links
        self.edge_right = rand_rechts

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
        logger.info(f"Aanvraag aangemaakt met L={self.edge_left} en R={self.edge_right}")
        logger.info(f"Werkruimte aangemaakt met L={self.werkruimte.edge_left} en R={self.werkruimte.edge_right}")
        # logger.info(f"Veiligheidsruimte aangemaakt met L={self.veiligheidsruimte.edge_left} "
        #             f"en R={self.veiligheidsruimte.edge_right}")
        # logger.info(f"Werkvak aangemaakt met L={self.werkvak.edge_left} en R={self.werkvak.edge_right}")


class Werkruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKRUIMTE
        self.request = request
        self.edge_left = request.edge_left
        self.edge_right = request.edge_right
        self.km = request.km

    def determine_minimal_werkruimte_size(self):
        left_request_lane_nr = self.request.edge_left[0]
        right_request_lane_nr = self.request.edge_right[0]

        lanes = self.request.road_info.obj_eigs
        all_lane_nrs = [lane_nr for lane_nr, lane_type in lanes.items() if isinstance(lane_nr, int) and
                        lane_type not in ["Puntstuk"]]
        main_lane_nrs = [lane_nr for lane_nr, lane_type in lanes.items() if isinstance(lane_nr, int) and
                         lane_type in ["Rijstrook", "Splitsing", "Samenvoeging", "Weefstrook"]]

        # In case the request is defined in terms of lanes on both sides...
        if left_request_lane_nr and right_request_lane_nr:
            assert left_request_lane_nr in main_lane_nrs, \
                ("Opgegeven rijstrooknummer voor rand links behoort niet tot de hoofdstroken.")
            assert right_request_lane_nr in main_lane_nrs, \
                ("Opgegeven rijstrooknummer voor rand rechts behoort niet tot de hoofdstroken.")

            # Determine if expansion is necessary
            if (min(all_lane_nrs) in [left_request_lane_nr, right_request_lane_nr]
                    or max(all_lane_nrs) in [left_request_lane_nr, right_request_lane_nr]):
                # The request goes all the way up to a side of the road. Expansion does not need to be determined.
                logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid.")
                return

            keep_left_open = True  # If False: keep right side open.

            n_main_lanes_left = left_request_lane_nr - min(main_lane_nrs)
            n_main_lanes_right = max(main_lane_nrs) - right_request_lane_nr

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
                self.edge_right = (max(all_lane_nrs), 0.0)
            else:
                # Adjust to far left side of road. Case TL2 or LL3
                self.edge_left = (min(all_lane_nrs), 0.0)
            return

        # In case the request is defined in lanes on one side
        if left_request_lane_nr or right_request_lane_nr:
            logger.warning("Deze situatie is nog niet uitgewerkt. Er wordt geen maatregel toegepast.")
            return

        # In case the request is not defined in lanes on either side
        over_24h = not self.request.under_24h
        left_request_space = self.edge_left[1]
        right_request_space = self.edge_right[1]

        assert left_request_space or right_request_space, "Specificeer hoeveelheid overgebleven ruimte in de aanvraag."

        # Case TL1:
        if self.request.under_24h and left_request_space and left_request_space >= -3.50:
            self.edge_right = (min(main_lane_nrs), -1.01)
            return

        # Case TR1:
        if self.request.under_24h and right_request_space and 1.10 < right_request_space <= self.request.sphere_of_influence:
            self.edge_left = (None, +1.01)
            return

        # Case LL1:
        if over_24h and left_request_space and left_request_space < -0.25:
            self.edge_right = (None, -1.01)
            return

        # Case TR2:
        if self.request.under_24h and right_request_space and 0.0 <= right_request_space <= 1.10:
            self.edge_left = (max(main_lane_nrs), +1.01)
            return

        # Case LL2:
        if over_24h and left_request_space and 0.0 >= left_request_space >= -0.25:
            self.edge_right = (None, -1.01)
            # And lane narrowing.
            return

        # Case LR1:
        if over_24h and right_request_space and 1.50 < right_request_space <= 2.50:
            self.edge_left = (None, +1.01)
            return

        # Case LR2:
        if over_24h and right_request_space and 0.0 <= right_request_space <= 1.50:
            self.edge_left = (max(main_lane_nrs), +1.0)
            # And lane narrowing.
            return

        logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid (geen effact op weg).")
        return

    def adjust_edges_to_veiligheidsruimte(self):
        return  # TODO

    def adjust_length_to_veiligheidsruimte(self):
        return  # TODO


class Veiligheidsruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = VEILIGHEIDSRUIMTE
        self.request = request
        self.edge_left = request.edge_left
        self.edge_right = request.edge_right
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
        self.edge_left = request.edge_left
        self.edge_right = request.edge_right
        self.km = request.km

    def adjust_edges_to_veiligheidsruimte(self):
        return  # TODO

    def adjust_edges_to_road(self):
        return  # TODO

    def adjust_length_to_msis(self):
        return  # TODO

