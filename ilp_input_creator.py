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
            road_dict[row.name]["MSI"][msi.lane_number]['Downstream']['Primary'] = msi.properties['d']
    return road_dict


def generate_file(dataset: dict, output_filename: str):
    with open(output_filename, "w") as outfile:
        json.dump(dataset, outfile, indent=2)
