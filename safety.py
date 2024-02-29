from functions import *


class Oppervlak:
    def __init__(self, km_start: float, km_end: float, width: list, roadside: str) -> None:
        self._km_start = km_start
        self._km_end = km_end
        self._width = width
        self._roadside = roadside
        print(self._width)

class Werkvak(Oppervlak):
    def __init__(self, km_start: float, km_end: float, lanes: list, roadside: str) -> None:
        width_1 = [(lane-1)*3.5 for lane in lanes]
        width_2 = [lane*3.5 for lane in lanes]
        widths = sorted(set(width_1 + width_2))
        width = [widths[0], widths[-1]]
        super().__init__(km_start, km_end, width, roadside)
        self._color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, wegmodel: WegModel, km_start: float, km_end: float, roadside: str,
                 ruimte_links: float = None, ruimte_midden: list = None, ruimte_rechts: float = None,
                 max_v: int = 70, afzetting: str = "Bakens") -> None:
        assert sum(1 for v in [ruimte_links, ruimte_midden, ruimte_rechts] if v is not None) == 1, "Specificeer één eis."

        # Obtain surrounding geometry and road properties
        # Temporary assumption: only one section below request
        road_info = wegmodel.get_section_info_at(km=km_start, side=roadside)
        road_lanes = [lane_nr for lane_nr, lane_type in road_info["Obj_eigs"] if isinstance(lane_nr, int)
                     and lane_type not in ['Puntstuk']]
        n_lanes = len(road_lanes)

        request_lanes = []

        if ruimte_links:
            if ruimte_links >= 3.50:
                print("Geen afzetting nodig.")
            else:
                # Case TL1
                request_lanes = [1]

        if ruimte_midden:
            a = min(ruimte_midden) - 1
            b = n_lanes - max(ruimte_midden)
            if a < b:
                request_lanes =
            else:
                request_lanes =

        if ruimte_rechts:
            if ruimte_rechts >= 8.00:  # Alpha: invloedssfeer van de weg
                print("Geen afzettingen nodig.")
            elif ruimte_rechts >= 1.10:
                # Case TR1
                request_lanes = [n_lanes]
            else:
                # Case TR2
                request_lanes = [n_lanes-1, n_lanes]

        super().__init__(km_start, km_end, request_lanes, roadside)

        self._color = "green"
        self._max_v = max_v
        self._afzetting = afzetting

        # Obtain minimal number of lanes for werkvak according to request

        # Initialise werkvak
        Werkvak(km_start, km_end, lanes_werkvak, roadside)


