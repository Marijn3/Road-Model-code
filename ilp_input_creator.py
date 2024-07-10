from msi_network import MSINetwerk
import json
import os
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


msi_dict = {
    "Downstream": {
        "Primary": None,
        "Secondary": None,
        "Taper": None,
        "Broadening": None,
        "Narrowing": None,
    },
    "Upstream": {
        "Primary": None,
        "Secondary": None,
        "Taper": None,
        "Broadening": None,
        "Narrowing": None,
    },
    "State": None,
    "Rush_hour_lane": None,
    "Exit-Entry": False,
    "TrafficStream": "1",
    "TrafficStream_Influence": {
        "Left": None,
        "Right": None
    },
    "Carriageway": "1"
}

msi_row_dict = {
    "MSI": {},
    "Continue-V": False,
    "Continue-X": False,
    "Stat-V": 130,
    "Dyn-V": None,
    "hard_shoulder": {
        "left": None,
        "right": None
    }
}


def transform_name(name: str) -> list | str | None:
    """
    Transform an MTM name to a name used as input for the ILP problem.
    Also takes lists of names and calls itself.
    Args:
        name (str): MTM form of name.
    Returns:
        Name in the form used by JvM.
    Example:
        transform_name("A2R:119.204:2") = [RSU_A2_R_119.204,2]
    """
    if name is None:
        return None

    if isinstance(name, list):
        return [transform_name(n) for n in name]

    road, km, msi_nr = name.split(":")
    if "_" not in road:
        road = f"{road[:-1]}_{road[-1]}"
    return f"[RSU_{road}_{km},{msi_nr}]"


def transform_row_name(name: str) -> list | str | None:
    """
    Transform an MTM row name to a row name used as input for the ILP problem.
    Args:
        name (str): MTM form of row name.
    Returns:
        Row name in the form used by JvM.
    Example:
        transform_row_name("A2R:119.204") = RSU_A2_R_119.204
        transform_row_name("A2_A:119.506") = RSU_A2_A_119.506
    """
    road, km = name.split(":")
    if "_" not in road:
        road = f"{road[:-1]}_{road[-1]}"
    return f"RSU_{road}_{km}"


def make_ILP_input(network: MSINetwerk) -> dict:
    """
    Generates ILP input file dictionary based on the framework provided by JvM.
    Args:
        network (MSINetwerk): A network of MSIs with all required properties.
    Returns:
        dictionary with required elements. Unspecified elements will contain None.
    """
    road_dict = {}

    # Extract road-related properties of the MSIs.
    for row in network.MSIrows:
        row_name = transform_row_name(row.name)
        road_dict[row_name] = deepcopy(msi_row_dict)

        for msi in row.MSIs.values():
            road_dict[row_name]["MSI"][msi.lane_nr] = deepcopy(msi_dict)
            road_dict[row_name]["MSI"][msi.lane_nr]["Rush_hour_lane"] = msi.properties["RHL"]
            road_dict[row_name]["MSI"][msi.lane_nr]["Exit-Entry"] = msi.properties["Exit_Entry"]
            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream"] = (
                str(msi.properties["TS_num"])) if msi.properties["TS_num"] else "99"
            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream_Influence"]["Left"] = msi.properties["DIF_V_left"]
            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream_Influence"]["Right"] = msi.properties["DIF_V_right"]
            road_dict[row_name]["MSI"][msi.lane_nr]["Carriageway"] = (
                str(msi.properties["CW_num"])) if msi.properties["CW_num"] else "99"

        # These properties are the same for the entire row, so the value taken from the last iteration.
        road_dict[row_name]["Continue-V"] = msi.properties["C_V"]
        road_dict[row_name]["Continue-X"] = msi.properties["C_X"]
        road_dict[row_name]["Stat-V"] = 100  # msi.properties["STAT_V"]
        # (overwritten because ILP does not expect speed below 100)
        road_dict[row_name]["Dyn-V"] = None  # msi.properties["DYN_V"]
        # (overwritten because this is used differently in request handling in ILP)
        road_dict[row_name]["hard_shoulder"]["left"] = msi.properties["Hard_shoulder_left"]
        road_dict[row_name]["hard_shoulder"]["right"] = msi.properties["Hard_shoulder_right"]

    relation_type_name_mapping = {"d": "Primary", "u": "Primary",
                                  "s": "Secondary", "t": "Taper", "b": "Broadening", "n": "Narrowing"}

    # Extract MSI relations from the (possibly edited) msi relations file.
    with open(network.profile.msi_relations_file, "r") as rel_file:
        lines = rel_file.readlines()

    for line in lines:
        start_msi, relation, end_msi = line.strip().split()

        road_nr, km, msi_nr = start_msi.split(":")
        row_name = transform_row_name(f"{road_nr}:{km}")
        direction = "Downstream" if "d" in relation else "Upstream"
        relation_name = relation_type_name_mapping[relation[-1]]

        road_dict[row_name]["MSI"][int(msi_nr)][direction][relation_name] = transform_name(end_msi)

    return road_dict


def generate_file(dataset: dict, output_folder: str):
    # Generate road model output folder if it does not exist.
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(f"{output_folder}/RoadModelMSINetwork.json", "w") as outfile:
        json.dump(dataset, outfile, indent=2)
