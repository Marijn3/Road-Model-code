from functions import *


class Oppervlak:
    def __init__(self, roadside: str, km_start: float, km_end: float, surf_type: str, width: list) -> None:
        self.roadside = roadside
        self.km_start = km_start
        self.km_end = km_end
        self.width = width
        self.surf_type = surf_type

        self.print_surface()

    def print_surface(self):
        print(f"Oppervlak '{self.surf_type}' gemaakt aan kant {self.roadside}, "
              f"van {self.km_start} tot {self.km_end}, met breedte {self.width}.")


class Werkvak(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: list) -> None:
        width_1 = [(lane-1)*3.5 for lane in lanes]
        width_2 = [lane*3.5 for lane in lanes]
        widths = sorted(set(width_1 + width_2))
        width = [widths[0], widths[-1]]
        super().__init__(roadside, km_start, km_end, "Werkvak", width)
        self.color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 ruimte_links: float = None, ruimte_midden: list = None, ruimte_rechts: float = None,
                 max_v: int = 70, duur_korter_24h: bool = True, afzetting: str = "Bakens") -> None:
        assert sum(1 for v in [ruimte_links, ruimte_midden, ruimte_rechts] if v is not None) == 1, "Specificeer één eis."

        self.wegmodel = wegmodel
        self.hectoletter = hectoletter
        self.ruimte_links = ruimte_links
        self.ruimte_midden = ruimte_midden
        self.ruimte_rechts = ruimte_rechts
        self.max_v = max_v
        self.duur_korter_24h = duur_korter_24h
        self.afzetting = afzetting
        self.color = "green"
        self.request_width = self.__determine_request_width()

        super().__init__(wegkant, km_start, km_end, "Aanvraag", self.request_width)

        self.__make_werkvak()

    def __determine_request_width(self) -> list:
        if self.ruimte_links:
            return [-1000, -self.ruimte_links]
        if self.ruimte_midden:
            width_1 = [(lane - 1) * 3.5 for lane in self.ruimte_midden]
            width_2 = [lane * 3.5 for lane in self.ruimte_midden]
            widths = sorted(set(width_1 + width_2))
            return [widths[0], widths[-1]]
        if self.ruimte_rechts:
            return [self.ruimte_rechts, 1000]

    def __make_werkvak(self):
        # Obtain surrounding geometry and road properties
        # Temporary assumption: only one section below request, section identified by km_start
        road_info = self.wegmodel.get_section_info_by_bps(km=self.km_start,
                                                          side=self.roadside,
                                                          hectoletter=self.hectoletter)

        if not road_info:
            raise Exception("Combinatie van km, wegkant en hectoletter niet gevonden!")

        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = self.__get_lanes_werkvak(road_info)

        # Initialise werkvak
        Werkvak(self.roadside, self.km_start, self.km_end, lanes_werkvak)

    def __get_lanes_werkvak(self, road_info: dict) -> list:
        all_lanes = [lane_nr for lane_nr, lane_type in road_info["Obj_eigs"].items() if isinstance(lane_nr, int)
                     and lane_type not in ["Puntstuk"]]

        main_lanes = [lane_nr for lane_nr, lane_type in road_info["Obj_eigs"].items() if isinstance(lane_nr, int)
                      and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging"]]

        lanes_left = all_lanes[:all_lanes.index(main_lanes[0])]
        lanes_right = all_lanes[all_lanes.index(main_lanes[-1])+1:]

        n_lanes = len(all_lanes)
        sphere_of_influence = 8.00  # Alpha: invloedssfeer van de weg TODO: Make dependent on road.

        if self.ruimte_midden:
            assert all(lane_nr in main_lanes for lane_nr in self.ruimte_midden), "Een aangevraagde rijstrook hoort niet bij de hoofdstroken."

            keep_left_open = True  # If False: keep right open.

            n_main_lanes_left = min(self.ruimte_midden) - 1
            n_main_lanes_right = n_lanes - max(self.ruimte_midden)
            if n_main_lanes_left < n_main_lanes_right:
                keep_left_open = False
            elif n_main_lanes_left == n_main_lanes_right:
                if road_info["Obj_eigs"][1] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = False
                if road_info["Obj_eigs"][n_lanes] in ["Vluchtstrook", "Spitsstrook", "Plusstrook"]:
                    keep_left_open = True
                # Desired result: if vluchtstrook on both sides and space equal, then left side should be open.
            else:
                keep_left_open = True

            if keep_left_open:
                return list(range(min(self.ruimte_midden), n_lanes + 1))  # Case TR3 or LR4
            else:
                return list(range(1, max(self.ruimte_midden) + 1))  # Case TL2 or LL3

        condition_tl_nothing = self.duur_korter_24h and self.ruimte_links and self.ruimte_links > 3.50
        condition_tl1 = self.duur_korter_24h and self.ruimte_links and self.ruimte_links <= 3.50

        condition_tr_nothing = self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts > sphere_of_influence
        condition_tr1 = self.duur_korter_24h and self.ruimte_rechts and 1.10 < self.ruimte_rechts <= sphere_of_influence
        condition_tr2 = self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.10

        condition_ll1 = not self.duur_korter_24h and self.ruimte_links and self.ruimte_links > 0.25
        condition_ll2 = not self.duur_korter_24h and self.ruimte_links and self.ruimte_links <= 0.25

        condition_lr_nothing = not self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts > 2.50
        condition_lr2 = not self.duur_korter_24h and self.ruimte_rechts and 1.50 < self.ruimte_rechts <= 2.50
        condition_lr3 = not self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.50

        if condition_tl_nothing or condition_tr_nothing or condition_lr_nothing:
            print("Geen afzettingen nodig.")
            return []

        if condition_tl1:
            return lanes_left

        if condition_tr1:
            return lanes_right

        if condition_tr2:
            return [min(lanes_right)-1] + lanes_right

        if condition_ll1:
            return lanes_left

        if condition_ll2:
            return lanes_left  # And lane narrowing

        if condition_lr2:
            return lanes_right

        if condition_lr3:
            return lanes_right  # And lane narrowing

        print("Deze code zou nooit moeten worden bereikt. Hoe dan ook, geen afzettingen nodig.")
        return []

