import json
from functions import *


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
        "right": True
    }
}


def make_ILP_input(network: MSINetwerk) -> dict:
    road_dict = {}
    for i_row, row in enumerate(network.MSIrows):
        road_dict[row.name] = deepcopy(msi_row_dict)
        for i_msi, msi in row.MSIs.items():
            road_dict[row.name]["MSI"][msi.lane_number] = deepcopy(msi_dict)
            road_dict[row.name]["MSI"][msi.lane_number]["Downstream"]["Primary"] = msi.properties["d"]
            road_dict[row.name]["MSI"][msi.lane_number]["Downstream"]["Secondary"] = msi.properties["ds"]

            road_dict[row.name]["MSI"][msi.lane_number]["Upstream"]["Primary"] = msi.properties["u"]
            road_dict[row.name]["MSI"][msi.lane_number]["Upstream"]["Secondary"] = msi.properties["us"]
            # More to be added as MSI data expands.
            
            road_dict[row.name]["MSI"][msi.lane_number]["Rush_hour_lane"] = msi.properties["RHL"]
            road_dict[row.name]["MSI"][msi.lane_number]["Exit-Entry"] = msi.properties["Exit_Entry"]

            road_dict[row.name]["MSI"][msi.lane_number]["TrafficStream"] = str(msi.properties["TS_num"])
            road_dict[row.name]["MSI"][msi.lane_number]["TrafficStream_Influence"]["Left"] = msi.properties["DIF_V_left"]
            road_dict[row.name]["MSI"][msi.lane_number]["TrafficStream_Influence"]["Right"] = msi.properties["DIF_V_right"]
            road_dict[row.name]["MSI"][msi.lane_number]["Carriageway"] = str(msi.properties["CW_num"])

        road_dict[row.name]["Continue-V"] = msi.properties["C_V"]
        road_dict[row.name]["Continue-X"] = msi.properties["C_X"]
        road_dict[row.name]["Stat-V"] = msi.properties["STAT_V"]

    return road_dict


def generate_file(dataset: dict, output_filename: str):
    with open(output_filename, "w") as outfile:
        json.dump(dataset, outfile, indent=2)
