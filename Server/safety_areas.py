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

    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 rand_links: tuple = None, rand_rechts: tuple = None,
                 maximumsnelheid: int = 70, korter_dan_24h: bool = True, afzetting: int = AFZETTING_BAKENS) -> None:
        assert rand_links or rand_rechts, "Specificeer minstens één eis."

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

        self.werkruimte = Werkruimte(self)
        self.veiligheidsruimte = Veiligheidsruimte(self)
        self.werkvak = Werkvak(self)

        self.step_1_determine_minimal_werkruimte()
        self.step_2_determine_area_sizes()
        self.step_3_determine_legend_request()
        self.step_4_solve_legend_request()
        self.step_5_adjust_area_sizes()

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


class Werkruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKRUIMTE
        self.request = request
        self.edge_left = request.edge_left
        self.edge_right = request.edge_right
        self.km = request.km

    def determine_minimal_werkruimte_size(self):
        return  # TODO

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

