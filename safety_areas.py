import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from road_model import WegModel
from utils import *

logger = logging.getLogger(__name__)

NEG_ZERO = -0.00001
POS_ZERO = 0.00001

AANVRAAG = 200
WERKRUIMTE = 201
VEILIGHEIDSRUIMTE = 202
WERKVAK = 203

COLORMAP = {
    AANVRAAG: "none",
    WERKVAK: "#13AFE1",
    VEILIGHEIDSRUIMTE: "#FBD799",
    WERKRUIMTE: "#F49510",
}

RUIMTE_NAMEN = {
    AANVRAAG: "Aanvraag",
    WERKVAK: "Werkvak",
    VEILIGHEIDSRUIMTE: "Veiligheidsruimte",
    WERKRUIMTE: "Werkruimte",
}

AREA_NAMES = {
    AANVRAAG: "Request",
    WERKVAK: "Closed space",
    VEILIGHEIDSRUIMTE: "Empty space",
    WERKRUIMTE: "Workspace",
}


class BREEDTE:
    BARRIER = 0.40  # Estimate, in meters
    GELEIDEBAKENS = 0.25  # Source: "WIU 2020 – Werken op autosnelwegen", p117, in meters
    RIJSTROOK = 3.50  # Estimate, in meters
    VLUCHTSTROOK = 2.00  # Estimate, in meters


class AFZETTINGEN:
    BAKENS = 300
    BARRIER_ONDER_80CM = 301
    BARRIER_BOVEN_80CM = 302


# Ruimte aan zijkanten van vakken in meters.
TUSSENRUIMTE_NAAST = {
    AFZETTINGEN.BAKENS: {WERKVAK: 0.5 * BREEDTE.GELEIDEBAKENS, VEILIGHEIDSRUIMTE: 0.60},
    AFZETTINGEN.BARRIER_ONDER_80CM: {WERKVAK: 0.5 * BREEDTE.BARRIER, VEILIGHEIDSRUIMTE: 0.60},
    AFZETTINGEN.BARRIER_BOVEN_80CM: {WERKVAK: 0.5 * BREEDTE.BARRIER, VEILIGHEIDSRUIMTE: 0.0},
}

# Ruimte aan voor- en achterkanten van vakken in kilometers.
TUSSENRUIMTE_VOOR = {
    WERKRUIMTE: 0.150,
    VEILIGHEIDSRUIMTE: 0.200
}

TUSSENRUIMTE_NA = {
    WERKRUIMTE: 0.000,
    VEILIGHEIDSRUIMTE: 0.050
}


class Rand:
    def __init__(self, rijstrook: int | None, afstand: float):
        self.lane = rijstrook
        self.distance = afstand

    def __repr__(self) -> str:
        position = f"Rijstrook {self.lane}" if self.lane else f"Naast weg"
        if self.distance > 0:
            return f"{position} +{round(self.distance, 2)}m"
        else:
            return f"{position} {round(self.distance, 2)}m"

    def move_edge(self, move_distance, lane_number_right_lane):
        if self.distance < 0 < self.distance + move_distance:  # The edge crosses 0
            self.lane = self.lane + 1 if self.lane else 1
        if self.distance > 0 > self.distance + move_distance:  # The edge crosses 0
            self.lane = self.lane - 1 if self.lane else lane_number_right_lane
        self.distance = round(self.distance + move_distance, 2)

    def make_simple_distance(self, n_lanes) -> float:
        if self.lane:
            n_full_lanes = self.lane - 1 if self.distance >= 0.0 else self.lane
        else:
            n_full_lanes = n_lanes if self.distance >= 0.0 else 0
        return n_full_lanes * BREEDTE.RIJSTROOK + round(self.distance, 2)


class Aanvraag:

    # Source: "WIU 2020 - Werken op autosnelwegen 03-10-2023 Rijkswaterstaat", p24
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

        logger.info(f"Aanvraag met kmrange={km_start} - {km_end} km en randen={randen}, korter dan 24h={korter_dan_24h}.")

        self.surface_type = AANVRAAG
        self.requires_lane_narrowing = False
        self.open_side = None

        self.sections = self.roadmodel.get_section_by_bps(self.km, self.roadside, self.hecto_character)
        if not self.sections:
            raise Exception(f"Combinatie van km, wegkant en hectoletter niet gevonden in wegmodel:\n"
                            f"{self.km} {self.roadside} {self.hecto_character}")

        # Temporary assumption: only one section below request (first section) TODO: Remove assumption.
        self.road_id = next(iter(self.sections.keys()))
        self.road_info = next(iter(self.sections.values()))
        self.n_lanes = self.road_info.verw_eigs.aantal_stroken
        self.sphere_of_influence = self.__SPHERE_OF_INFLUENCE.get(self.road_info.obj_eigs["Maximumsnelheid"], None)

        self.lanes = self.road_info.obj_eigs
        self.all_lane_nrs = [lane_nr for lane_nr, lane_type in self.lanes.items() if isinstance(lane_nr, int) and
                             lane_type not in ["Puntstuk"]]
        self.main_lane_nrs = [lane_nr for lane_nr, lane_type in self.lanes.items() if isinstance(lane_nr, int) and
                              lane_type not in ["Puntstuk", "Vluchtstrook", "Spitsstrook", "Plusstrook"]]
        self.first_lane_nr = min(self.all_lane_nrs)
        self.last_lane_nr = max(self.all_lane_nrs)
        self.n_main_lanes = len(self.main_lane_nrs)

        self.msis_red_cross = []
        self.measure_request = {}

        self.werkruimte = Werkruimte(self)
        self.veiligheidsruimte = Veiligheidsruimte(self)
        self.werkvak = Werkvak(self)

        self.step_1_determine_initial_workspace()
        self.step_2_determine_area_sizes()
        self.step_3_generate_measure_request()
        # self.step_4_solve_measure_request()
        # self.step_5_adjust_area_sizes()

        self.report_request()

    def run_sanity_checks(self):
        assert len(self.edges) == 2, \
            "Specificeer beide randen."
        assert self.edges["L"].distance and self.edges["R"].distance, \
            "Specificeer afstand vanaf belijning in de aanvraag."
        assert abs(self.edges["L"].distance) != abs(self.edges["R"].distance), \
            "Specificeer ongelijke afstanden."  # TODO: Specify when this is an issue

    def step_1_determine_initial_workspace(self):
        self.werkruimte.determine_minimal_werkruimte_size()

    def step_2_determine_area_sizes(self):
        # Determine minimal width from the original area
        self.veiligheidsruimte.adjust_edges_to_werkruimte()
        self.werkvak.adjust_edges_to_veiligheidsruimte()

        # Determine convenient width in regard to the road
        self.werkvak.adjust_edges_to_road()
        self.veiligheidsruimte.adjust_edges_to_werkvak()
        self.werkruimte.adjust_edges_to_veiligheidsruimte()

        # Determine minimal length with respect to the MSIs
        self.werkvak.adjust_length_to_msis()
        self.veiligheidsruimte.adjust_length_to_werkvak()
        self.werkruimte.adjust_length_to_veiligheidsruimte()

        self.plot_areas()

    def step_3_generate_measure_request(self):
        self.msis_red_cross = self.werkvak.obtain_msis_inside()
        self.measure_request = self.werkvak.determine_measure_request()

    def step_4_solve_measure_request(self):
        logger.info(f"The following should be sent to ILP:\n{self.measure_request}")
        return  # TODO

    def step_5_adjust_area_sizes(self):
        return  # TODO

    def plot_areas(self):
        fig = plt.figure()
        ax = fig.add_subplot()

        x_min = -3
        x_max = len(self.all_lane_nrs) * 3.5 + 1.5
        # x_max = self.werkvak.edges["R"].make_simple_distance(self.n_main_lanes) + 2
        y_min = self.werkvak.km[0] - 0.10
        y_max = self.werkvak.km[1] + 0.10

        plt.xlim([x_min, x_max])
        plt.ylim([y_min, y_max])
        plt.xlabel("Width [m] (estimate for visualization)")
        plt.ylabel("Length [km]")
        plt.title(f"Safety areas for request with category {self.werkruimte.category}")

        for lane_number in self.all_lane_nrs:
            south = y_min
            west = (lane_number - 1) * BREEDTE.RIJSTROOK
            if lane_number not in self.main_lane_nrs:
                if lane_number == 1:
                    west += (BREEDTE.VLUCHTSTROOK - BREEDTE.RIJSTROOK)
                width = BREEDTE.VLUCHTSTROOK
                color = "darkgrey"
            else:
                width = BREEDTE.RIJSTROOK
                color = "lightgrey"
            lane = matplotlib.patches.Rectangle(xy=(west + 0.05, south),
                                                width=width - 0.1,
                                                height=y_max - y_min,
                                                facecolor=color)
            ax.add_patch(lane)

        self.plot_area(ax, self.werkvak)
        self.plot_area(ax, self.veiligheidsruimte)
        self.plot_area(ax, self.werkruimte)
        self.plot_area(ax, self)

        ax.legend()
        plt.show()

    def plot_area(self, ax, area):
        x = area.edges["L"].make_simple_distance(self.n_main_lanes)
        y = area.edges["R"].make_simple_distance(self.n_main_lanes)

        edgecolor = "brown" if area.surface_type == AANVRAAG else "none"

        rect = matplotlib.patches.Rectangle(xy=(x, area.km[0]),
                                            width=y-x,
                                            height=area.km[1]-area.km[0],
                                            facecolor=COLORMAP[area.surface_type],
                                            edgecolor=edgecolor,
                                            linewidth=2.0,
                                            label=AREA_NAMES[area.surface_type])
        ax.add_patch(rect)

    def report_request(self):
        logger.info(f"Aanvraag aangemaakt met km {self.km} en randen {self.edges}")
        logger.info(f"Werkruimte aangemaakt met km {self.werkruimte.km} en randen {self.werkruimte.edges}")
        logger.info(f"Veiligheidsruimte aangemaakt met km {self.veiligheidsruimte.km} en randen {self.veiligheidsruimte.edges}")
        logger.info(f"Werkvak aangemaakt met km {self.werkvak.km} en randen {self.werkvak.edges}\n")


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
            self.make_edge(side=self.request.open_side, lane=None, distance_r=-0.81)
        elif self.category == "B":
            self.make_edge(side=self.request.open_side, lane=min(self.request.main_lane_nrs), distance_r=-0.81)
        elif self.category == "C":
            self.request.requires_lane_narrowing = True
            self.make_edge(side=self.request.open_side, lane=None, distance_r=NEG_ZERO)
        elif self.category == "D":
            other_side = "R" if self.request.open_side == "L" else "L"
            self.make_edge(side=other_side, lane=None, distance_r=+BREEDTE.VLUCHTSTROOK)

    def make_edge(self, side: str, lane: int | None, distance_r: float) -> None:
        if side == "L":
            distance_r = -distance_r
        self.edges[side] = Rand(rijstrook=lane, afstand=+distance_r)

    def determine_request_category_onroad(self) -> None:
        self.do_onroad_sanity_checks()
        self.category = "D"

        # Determine if expansion is not necessary. When the request goes all the way up
        # to a side of the road, expansion of the request does not need to be determined.
        if self.request.first_lane_nr in [self.request.edges["L"].lane, self.request.edges["R"].lane]:
            logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid.")
            self.request.open_side = "R"
            return
        if self.request.last_lane_nr in [self.request.edges["L"].lane, self.request.edges["R"].lane]:
            logger.info("De randen van deze aanvraag hoeven niet te worden uitgebreid.")
            self.request.open_side = "L"
            return

        self.request.open_side = self.determine_open_side()

    def do_onroad_sanity_checks(self) -> None:
        assert self.request.edges["L"].lane is None or self.request.edges["L"].lane in self.request.main_lane_nrs, \
            "Opgegeven rijstrooknummer voor rand links behoort niet tot de hoofdstroken."
        assert self.request.edges["R"].lane is None or self.request.edges["R"].lane in self.request.main_lane_nrs, \
            "Opgegeven rijstrooknummer voor rand rechts behoort niet tot de hoofdstroken."
        assert self.request.edges["L"].distance is None or self.request.edges["L"].distance >= 0, \
            "Geef een positieve afstand voor de linkerrand op."
        assert self.request.edges["R"].distance is None or self.request.edges["R"].distance <= 0, \
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

    def determine_request_category_roadside(self) -> None:
        if abs(self.edges["L"].distance) < abs(self.edges["R"].distance):
            crit_dist = self.edges["L"].distance  # Space closest to road
        else:
            crit_dist = self.edges["R"].distance

        if self.edges["L"].distance >= 0 and self.edges["R"].distance >= 0:
            side_of_road = "R"
            self.request.open_side = "L"
        elif self.edges["L"].distance <= 0 and self.edges["R"].distance <= 0:
            crit_dist = -crit_dist  # Obtain positive distance
            side_of_road = "L"
            self.request.open_side = "R"
        else:
            raise Exception("Deze combinatie van randen is niet toegestaan.")

        if not crit_dist >= 0.0:
            logger.warning(f"Critical distance below 0 ({crit_dist}), this leads to erroneous behaviour.")

        if ((self.request.under_24h and side_of_road == "R" and 1.10 < crit_dist <= self.request.sphere_of_influence)
                or (self.request.under_24h and side_of_road == "L" and 1.10 < crit_dist <= 3.50)
                or (not self.request.under_24h and side_of_road == "L" and 0.25 < crit_dist)
                or (not self.request.under_24h and side_of_road == "R" and 0.25 < crit_dist <= 2.50)):
            self.category = "A"

        elif ((self.request.under_24h and side_of_road == "L" and 0.0 <= crit_dist <= 1.1)
                or (self.request.under_24h and side_of_road == "R" and 0.0 <= crit_dist <= 1.10)):
            self.category = "B"

        elif ((not self.request.under_24h and side_of_road == "L" and 0.0 <= crit_dist <= 0.25)
                or (not self.request.under_24h and side_of_road == "R" and 0.0 <= crit_dist <= 0.25)):
            self.category = "C"

        else:
            logger.info("Geen passende categorie gevonden voor de gegeven aanvraag.")

    def adjust_edges_to_veiligheidsruimte(self):
        adjust_edges_to(self.request.veiligheidsruimte, self, VEILIGHEIDSRUIMTE, away_from=False)

    def adjust_length_to_veiligheidsruimte(self):
        adjust_length_to(self.request.veiligheidsruimte, self)


class Veiligheidsruimte:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = VEILIGHEIDSRUIMTE
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_werkruimte(self) -> None:
        adjust_edges_to(self.request.werkruimte, self, self.surface_type, away_from=True)

    def adjust_edges_to_werkvak(self) -> None:
        adjust_edges_to(self.request.werkvak, self, WERKVAK, away_from=False)

    def adjust_length_to_werkvak(self) -> None:
        adjust_length_to(self.request.werkvak, self)


class Werkvak:
    def __init__(self, request: Aanvraag) -> None:
        self.surface_type = WERKVAK
        self.request = request
        self.edges = deepcopy(request.edges)
        self.km = request.km

    def adjust_edges_to_veiligheidsruimte(self) -> None:
        adjust_edges_to(self.request.veiligheidsruimte, self, self.surface_type, away_from=True)

    def adjust_edges_to_road(self) -> None:
        if not self.request.requires_lane_narrowing:
            if self.request.open_side == "L":
                self.edges["L"].distance = POS_ZERO
            if self.request.open_side == "R":
                self.edges["R"].distance = NEG_ZERO

    def adjust_length_to_msis(self) -> None:
        current_closest_higher_km = float("inf")
        current_closest_lower_km = float("-inf")
        msi_at_higher_km = None
        msi_at_lower_km = None

        if self.request.roadside == "R":
            open_space_high_km = TUSSENRUIMTE_NA[WERKRUIMTE] + TUSSENRUIMTE_NA[VEILIGHEIDSRUIMTE]
            open_space_low_km = TUSSENRUIMTE_VOOR[WERKRUIMTE] + TUSSENRUIMTE_VOOR[VEILIGHEIDSRUIMTE]
        else:
            open_space_low_km = TUSSENRUIMTE_NA[WERKRUIMTE] + TUSSENRUIMTE_NA[VEILIGHEIDSRUIMTE]
            open_space_high_km = TUSSENRUIMTE_VOOR[WERKRUIMTE] + TUSSENRUIMTE_VOOR[VEILIGHEIDSRUIMTE]

        for msi_info in self.request.roadmodel.get_points_info("MSI"):
            if self.km[1] + open_space_high_km < msi_info.pos_eigs.km < current_closest_higher_km:
                current_closest_higher_km = msi_info.pos_eigs.km
                msi_at_higher_km = msi_info
            if current_closest_lower_km < msi_info.pos_eigs.km < self.km[0] - open_space_low_km:
                current_closest_lower_km = msi_info.pos_eigs.km
                msi_at_lower_km = msi_info

        if not msi_at_higher_km or not msi_at_lower_km:
            raise NotImplementedError("Geen passende signalering gevonden.")

        self.km = [msi_at_lower_km.pos_eigs.km, msi_at_higher_km.pos_eigs.km]

    def obtain_msis_inside(self) -> list[tuple]:
        # Determine fully covered lanes
        lane = {"L": None, "R": None}
        for side in lane.keys():
            if self.edges[side].lane:
                if not self.request.requires_lane_narrowing:
                    lane[side] = self.edges[side].lane
                else:
                    lane[side] = self.edges[side].lane + 1 if side == "L" else self.edges[side].lane - 1
            else:
                if self.edges[side].distance < 0.0:
                    lane[side] = min(self.request.main_lane_nrs) - 1
                else:
                    lane[side] = max(self.request.main_lane_nrs) + 1

        covered_lanes = [lane_number for lane_number in range(lane["L"], lane["R"] + 1)]
        lanes_for_crosses = [lane_nr for lane_nr in covered_lanes if lane_nr in self.request.all_lane_nrs]

        # Determine MSI rows
        msi_rows_inside = []
        if self.request.roadside == "R":
            for msi_info in self.request.roadmodel.get_points_info("MSI"):
                if self.km[0] <= msi_info.pos_eigs.km < self.km[1]:
                    msis_for_crosses = [nr for nr in lanes_for_crosses if nr in msi_info.obj_eigs["Rijstrooknummers"]]
                    msi_rows_inside.append((msi_info, msis_for_crosses))
        else:  # roadside == "L"
            for msi_info in self.request.roadmodel.get_points_info("MSI"):
                if self.km[0] < msi_info.pos_eigs.km <= self.km[1]:
                    msis_for_crosses = [nr for nr in lanes_for_crosses if nr in msi_info.obj_eigs["Rijstrooknummers"]]
                    msi_rows_inside.append((msi_info, msis_for_crosses))

        return msi_rows_inside

    def determine_measure_request(self) -> dict:
        # See report JvM page 71 for an explanation of this request structure
        request = {
            "name": "custom request",
            "type": "add",
            "legend_requests": [],
            "options": {}
        }

        for msi, lane_nrs in self.request.msis_red_cross:
            if not lane_nrs:
                continue
            for lane_nr in lane_nrs:
                request["legend_requests"].append(f"x[{make_ILP_name(msi, lane_nr)}]")
        return request


def make_ILP_name(point_info, nr) -> str:
    """
    Makes MSI name using the ILP convention used in the project of Jeroen van Meurs.
    """
    if point_info.pos_eigs.hectoletter:
        return (f"RSU_{point_info.pos_eigs.wegnummer}_"
                f"{point_info.pos_eigs.hectoletter.upper()}_"
                f"{point_info.pos_eigs.km:.3f},{nr}")
    else:
        return (f"RSU_{point_info.pos_eigs.wegnummer}_"
                f"{point_info.pos_eigs.rijrichting}_"
                f"{point_info.pos_eigs.km:.3f},{nr}")


def adjust_edges_to(area_to_base_on, area, border_surface, away_from: bool):
    area.edges = deepcopy(area_to_base_on.edges)
    direction = 1 if ((area.request.open_side == "R" and away_from) or
                      (area.request.open_side == "L" and not away_from)) else -1

    move_distance = direction * TUSSENRUIMTE_NAAST[area.request.demarcation][border_surface]
    area.edges[area.request.open_side].move_edge(move_distance, max(area.request.main_lane_nrs))


def adjust_length_to(area_to_adjust_to, area):
    if area.request.roadside == "R":
        open_space_high_km = TUSSENRUIMTE_NA[area.surface_type]
        open_space_low_km = TUSSENRUIMTE_VOOR[area.surface_type]
    else:
        open_space_low_km = TUSSENRUIMTE_NA[area.surface_type]
        open_space_high_km = TUSSENRUIMTE_VOOR[area.surface_type]

    area.km = [round(area_to_adjust_to.km[0] + open_space_low_km, 3),
               round(area_to_adjust_to.km[1] - open_space_high_km, 3)]
