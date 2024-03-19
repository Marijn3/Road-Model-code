import json
from safety import *


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
    return f"[RSU_{road[:-1]}_{road[-1]}_{km},{msi_nr}]"


def transform_row_name(name: str) -> list | str | None:
    """
    Transform an MTM row name to a row name used as input for the ILP problem.
    Args:
        name (str): MTM form of row name.
    Returns:
        Row name in the form used by JvM.
    Example:
        transform_name("A2R:119.204") = RSU_A2_R_119.204
        transform_name("A2_A:119.204") = RSU_A2_A_119.204
    """
    road, km = name.split(":")
    if "_" not in road:
        return f"RSU_{road[:-1]}_{road[-1]}_{km}"
    return f"RSU_{road}_{km}"


def make_ILP_input(network: MSINetwerk) -> dict:
    """
    Generates ILP input file dictionary based on framework provided by JvM.
    Args:
        network (MSINetwerk): A network of MSIs with all required properties.
    Returns:
        dictionary with required elements. Unspecified elements will contain None.
    """
    road_dict = {}

    for i_row, row in enumerate(network.MSIrows):
        row_name = transform_row_name(row.name)
        road_dict[row_name] = deepcopy(msi_row_dict)

        for i_msi, msi in row.MSIs.items():
            road_dict[row_name]["MSI"][msi.lane_nr] = deepcopy(msi_dict)
            road_dict[row_name]["MSI"][msi.lane_nr]["Downstream"]["Primary"] = transform_name(msi.properties["d"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Downstream"]["Secondary"] = transform_name(msi.properties["ds"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Downstream"]["Taper"] = transform_name(msi.properties["dt"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Downstream"]["Broadening"] = transform_name(msi.properties["db"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Downstream"]["Narrowing"] = transform_name(msi.properties["dn"])

            road_dict[row_name]["MSI"][msi.lane_nr]["Upstream"]["Primary"] = transform_name(msi.properties["u"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Upstream"]["Secondary"] = transform_name(msi.properties["us"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Upstream"]["Taper"] = transform_name(msi.properties["ut"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Upstream"]["Broadening"] = transform_name(msi.properties["ub"])
            road_dict[row_name]["MSI"][msi.lane_nr]["Upstream"]["Narrowing"] = transform_name(msi.properties["un"])
            
            road_dict[row_name]["MSI"][msi.lane_nr]["Rush_hour_lane"] = msi.properties["RHL"]
            road_dict[row_name]["MSI"][msi.lane_nr]["Exit-Entry"] = msi.properties["Exit_Entry"]

            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream"] = str(msi.properties["TS_num"])
            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream_Influence"]["Left"] = msi.properties["DIF_V_left"]
            road_dict[row_name]["MSI"][msi.lane_nr]["TrafficStream_Influence"]["Right"] = msi.properties["DIF_V_right"]
            road_dict[row_name]["MSI"][msi.lane_nr]["Carriageway"] = str(msi.properties["CW_num"])

        road_dict[row_name]["Continue-V"] = msi.properties["C_V"]
        road_dict[row_name]["Continue-X"] = msi.properties["C_X"]
        road_dict[row_name]["Stat-V"] = msi.properties["STAT_V"]
        road_dict[row_name]["Dyn-V"] = msi.properties["DYN_V"]
        road_dict[row_name]["hard_shoulder"]["left"] = msi.properties["Hard_shoulder_left"]
        road_dict[row_name]["hard_shoulder"]["right"] = msi.properties["Hard_shoulder_right"]

    return road_dict


def generate_file(dataset: dict, output_filename: str):
    with open(output_filename, "w") as outfile:
        json.dump(dataset, outfile, indent=2)
