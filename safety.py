from functions import *


class Oppervlak:
    def __init__(self, km_start: float, km_end: float, lanes: list, roadside: str) -> None:
        self._km_start = km_start
        self._km_end = km_end
        self._lanes = lanes
        self._roadside = roadside


class Werkvak(Oppervlak):
    def __init__(self, km_start: float, km_end: float, lanes: list, roadside: str) -> None:
        super().__init__(km_start, km_end, lanes, roadside)
        self._color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, wegmodel: WegModel, km_start: float, km_end: float,
                 lanes: list, roadside: str, max_v: int, afzetting: str) -> None:
        super().__init__(km_start, km_end, lanes, roadside)
        self._color = "green"
        self._max_v = max_v
        self._afzetting = afzetting

        # Obtain surrounding geometry and road properties
        wegmodel.get_section_info_at(km=km_start, side=roadside)  # Temporary assumption: only one section below request

        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = []

        # Initialise werkvak
        Werkvak(km_start, km_end, lanes_werkvak, roadside)


