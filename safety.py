from functions import *


class Oppervlak:
    def __init__(self, roadside: str, km_start: float, km_end: float, width: list) -> None:
        self._km_start = km_start
        self._km_end = km_end
        self._width = width
        self._roadside = roadside
        print(self._width)


class Werkvak(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: list) -> None:
        width_1 = [(lane-1)*3.5 for lane in lanes]
        width_2 = [lane*3.5 for lane in lanes]
        widths = sorted(set(width_1 + width_2))
        width = [widths[0], widths[-1]]
        super().__init__(roadside, km_start, km_end, width)
        self._color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 ruimte_links: float = None, ruimte_midden: list = None, ruimte_rechts: float = None,
                 max_v: int = 70, maatregel_korter_24h: bool = True, afzetting: str = "Bakens") -> None:
        assert sum(1 for v in [ruimte_links, ruimte_midden, ruimte_rechts] if v is not None) == 1, "Specificeer één eis."

        self.wegmodel = wegmodel
        self.km_start = km_start
        self.km_end = km_end
        self.wegkant = wegkant
        self.hectoletter = hectoletter
        self.ruimte_links = ruimte_links
        self.ruimte_midden = ruimte_midden
        self.ruimte_rechts = ruimte_rechts
        self.max_v = max_v
        self.maatregel_korter_24h = maatregel_korter_24h
        self.afzetting = afzetting
        self.color = "green"
        self.request_width = self.__determine_request_width()

        super().__init__(self.wegkant, self.km_start, self.km_end, self.request_width)

        self.__make_werkvak()

    def __determine_request_width(self) -> list:
        if self.ruimte_links:
            return [-self.ruimte_links - 3.5, -self.ruimte_links]
        if self.ruimte_midden:
            width_1 = [(lane - 1) * 3.5 for lane in self.ruimte_midden]
            width_2 = [lane * 3.5 for lane in self.ruimte_midden]
            widths = sorted(set(width_1 + width_2))
            return [widths[0], widths[-1]]
        if self.ruimte_rechts:
            return [self.ruimte_rechts, self.ruimte_rechts + 3.5]

    def __make_werkvak(self):
        # Obtain surrounding geometry and road properties
        # Temporary assumption: only one section below request, section identified by km_start
        road_info = self.wegmodel.get_section_info_by_bps(km=self.km_start,
                                                          side=self.wegkant,
                                                          hectoletter=self.hectoletter)

        if not road_info:
            raise Exception("Combinatie van km, wegkant en hectoletter niet gevonden!")

        road_lanes = [lane_nr for lane_nr, lane_type in road_info["Obj_eigs"] if isinstance(lane_nr, int)
                      and lane_type not in ['Puntstuk']]
        n_lanes = len(road_lanes)

        sphere_of_influence = 8.00  # Alpha: invloedssfeer van de weg TODO: Make dependent on road.

        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = self.__get_lanes_werkvak(n_lanes, sphere_of_influence)

        # Initialise werkvak
        Werkvak(self.wegkant, self.km_start, self.km_end, lanes_werkvak)

    def __get_lanes_werkvak(self, n_lanes: int, sphere_of_influence: float) -> list:
        if self.maatregel_korter_24h:
            if self.ruimte_links:
                if self.ruimte_links >= 3.50:
                    print("Geen afzettingen nodig.")
                    return []
                else:
                    return [1]  # Case TL1

            if self.ruimte_midden:
                a = min(self.ruimte_midden) - 1
                b = n_lanes - max(self.ruimte_midden)
                if a < b:
                    return list(range(1, max(self.ruimte_midden) + 1))  # Case TL2
                else:
                    return list(range(min(self.ruimte_midden), n_lanes + 1))  # Case TR3

            if self.ruimte_rechts:
                if self.ruimte_rechts >= sphere_of_influence:
                    print("Geen afzettingen nodig.")
                    return []
                elif self.ruimte_rechts >= 1.10:

                    return [n_lanes]  # Case TR1
                else:
                    return [n_lanes - 1, n_lanes]  # Case TR2
        else:  # Measure longer than day
            if self.ruimte_links:
                if self.ruimte_links >= 0.25:
                    return [1]  # LL1
                else:
                    return [1, 2]  # Case LL2

            if self.ruimte_midden:
                a = min(self.ruimte_midden) - 1
                b = n_lanes - max(self.ruimte_midden)
                if a < b:
                    return list(range(1, max(self.ruimte_midden) + 1))  # Case LL3
                else:
                    return list(range(min(self.ruimte_midden), n_lanes + 1))  # Case LR4

            if self.ruimte_rechts:
                if self.ruimte_rechts >= 2.50:  # Alpha: invloedssfeer van de weg
                    print("Geen afzettingen nodig.")
                    return []  # Case LR1
                elif self.ruimte_rechts >= 1.00:
                    return [n_lanes]  # Case LR2
                else:
                    return [n_lanes - 1, n_lanes]  # Case LR3

        print("Deze code zou nooit moeten worden bereikt.")
        return []



