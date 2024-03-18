from functions import *


class Oppervlak:
    def __init__(self, roadside: str, km_start: float, km_end: float, surf_type: str, unfiltered_lanes: dict) -> None:
        self.roadside = roadside
        self.km_start = km_start
        self.km_end = km_end
        self.surf_type = surf_type
        self.lanes = {lane_nr: lane_type for lane_nr, lane_type in unfiltered_lanes.items() if isinstance(lane_nr, int)}
        self.width = self.get_width()

        self.print_surface()

    def print_surface(self):
        print(f"Oppervlak '{self.surf_type}' gemaakt aan kant {self.roadside}, "
              f"van {self.km_start} tot {self.km_end}, met stroken {self.lanes} en breedte {self.width}.")

    def get_width(self) -> list:
        lane_numbers = self.lanes.keys()
        min_width = min((lane - 1) * 3.5 for lane in lane_numbers)
        max_width = max(lane * 3.5 for lane in lane_numbers)
        return [min_width, max_width]


class Werkvak(Oppervlak):
    def __init__(self, roadside: str, km_start: float, km_end: float, lanes: dict) -> None:
        super().__init__(roadside, km_start, km_end, "Werkvak", lanes)
        self.color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, wegmodel: WegModel, wegkant: str, km_start: float, km_end: float, hectoletter: str = "",
                 ruimte_links: float = None, ruimte_midden: list = None, ruimte_rechts: float = None,
                 max_v: int = 70, duur_korter_24h: bool = True, afzetting: str = "Bakens") -> None:
        assert sum(1 for v in [ruimte_links, ruimte_midden, ruimte_rechts] if v is not None) == 1, "Specificeer één eis."
        assert not ruimte_links or (ruimte_links and ruimte_links > 0), "Onjuiste aanvraag. Definieer positieve afstanden."
        assert not ruimte_rechts or (ruimte_rechts and ruimte_rechts > 0), "Onjuiste aanvraag. Definieer positieve afstanden."

        self.wegmodel = wegmodel
        self.hectoletter = hectoletter
        self.ruimte_links = ruimte_links
        self.ruimte_midden = ruimte_midden
        self.ruimte_rechts = ruimte_rechts
        self.max_v = max_v
        self.duur_korter_24h = duur_korter_24h
        self.afzetting = afzetting
        self.color = "green"

        self.road_info = self.get_road_info(km_start, wegkant, hectoletter)

        self.all_lanes = list(sorted([lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items() if isinstance(lane_nr, int) and lane_type not in "Puntstuk"]))
        self.main_lanes = [lane_nr for lane_nr, lane_type in self.road_info.obj_eigs.items()
                           if isinstance(lane_nr, int) and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging"]]

        self.lane_nrs_left = self.all_lanes[:self.all_lanes.index(self.main_lanes[0])]
        self.lanes_left = self.filter_lanes(self.lane_nrs_left)
        self.lane_nrs_right = self.all_lanes[self.all_lanes.index(self.main_lanes[-1])+1:]
        self.lanes_right = self.filter_lanes(self.lane_nrs_right)

        # if self.ruimte_links and not self.lane_nrs_left: ...

        self.lane_nrs_right_tr2 = self.all_lanes[self.all_lanes.index(self.main_lanes[-1]):]
        self.lanes_right_tr2 = self.filter_lanes(self.lane_nrs_right)

        self.request_lanes = self.determine_request_lanes()

        super().__init__(wegkant, km_start, km_end, "Aanvraag", self.request_lanes)

        self.n_lanes = len(self.all_lanes)
        self.sphere_of_influence = 8.00  # Alpha: invloedssfeer van de weg TODO: Make dependent on road.

        self.__make_werkvak()

    def filter_lanes(self, lane_nrs: list) -> dict:
        return {lane_nr: lane_type for lane_nr, lane_type in self.road_info.obj_eigs.items()
                if lane_nr in lane_nrs and lane_type not in ["Puntstuk"]}

    def get_road_info(self, km_start, roadside, hectoletter) -> ObjectInfo:
        # Obtain surrounding geometry and road properties
        # Temporary assumption: only one section below request, section identified by km_start
        road_info = self.wegmodel.get_section_info_by_bps(km=km_start,
                                                          side=roadside,
                                                          hectoletter=hectoletter)

        if not road_info:
            raise Exception("Combinatie van km, wegkant en hectoletter niet gevonden!")

        return road_info

    def determine_request_lanes(self) -> dict:
        if self.ruimte_links:
            return self.lanes_left
        if self.ruimte_midden:
            assert all(lane_nr in self.main_lanes for lane_nr in self.ruimte_midden), \
                "Een aangevraagde rijstrook hoort niet bij de hoofdstroken."
            return self.filter_lanes(self.ruimte_midden)
        if self.ruimte_rechts:
            return self.lanes_right

    def __make_werkvak(self):
        # Obtain minimal number of lanes for werkvak according to request
        lanes_werkvak = self.__get_lanes_werkvak(self.road_info)

        # Initialise werkvak
        if lanes_werkvak:
            Werkvak(self.roadside, self.km_start, self.km_end, lanes_werkvak)
        else:
            print("Geen afzettingen nodig voor deze aanvraag.")

    def __get_lanes_werkvak(self, road_info: dict) -> dict:
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
                return self.filter_lanes(list(range(min(self.ruimte_midden), self.n_lanes + 1)))  # Case TR3 or LR4
            else:
                return self.filter_lanes(list(range(1, max(self.ruimte_midden) + 1)))  # Case TL2 or LL3

        condition_tl1 = self.duur_korter_24h and self.ruimte_links and self.ruimte_links <= 3.50

        condition_tr1 = self.duur_korter_24h and self.ruimte_rechts and 1.10 < self.ruimte_rechts <= self.sphere_of_influence
        condition_tr2 = self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.10

        condition_ll1 = not self.duur_korter_24h and self.ruimte_links and self.ruimte_links > 0.25
        condition_ll2 = not self.duur_korter_24h and self.ruimte_links and self.ruimte_links <= 0.25

        condition_lr2 = not self.duur_korter_24h and self.ruimte_rechts and 1.50 < self.ruimte_rechts <= 2.50
        condition_lr3 = not self.duur_korter_24h and self.ruimte_rechts and self.ruimte_rechts <= 1.50

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

