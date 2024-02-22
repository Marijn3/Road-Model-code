import copy
import json

# <----- set options below -----> #

n_rsu = 20
n_msi = 8

data_file = "Server/Data/Large_road_2/input_data.json"

# <----- set options above -----> #



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

road_dict = {}

RSU_dict = {
        "MSI": {},
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 130,
        "Dyn-V": None,
        "hard_shoulder" : {
            "left": None,
            "right":True
        }
    }

def createDataSet(n_rsu,n_msi):
  
  for i in range(n_rsu):
    RSU = f"RSU_A684_L_{i}_0"
    road_dict[RSU] = copy.deepcopy(RSU_dict)

    if i > 0:
        RSU_u = f"RSU_A684_L_{i-1}_0"
    if i < n_rsu-1:
        RSU_d = f"RSU_A684_L_{i+1}_0"

    for j in range(n_msi):
        road_dict[RSU]["MSI"][j+1] = copy.deepcopy(msi_dict)
        if i > 0:
          MSI_u = f"[{RSU_u},{j+1}]"
          road_dict[RSU]["MSI"][j+1]["Upstream"]["Primary"] = MSI_u
        if i < n_rsu-1:
          MSI_d = f"[{RSU_d},{j+1}]"
          road_dict[RSU]["MSI"][j+1]["Downstream"]["Primary"] = MSI_d
        if j > 3:
            road_dict[RSU]["MSI"][j+1]["Carriageway"] = "2"
            road_dict[RSU]["MSI"][j+1]["TrafficStream"] = "2"
            road_dict[RSU]["MSI"][j+1]["TrafficStream_Influence"]["Left"] = 0
        if j < 4:
            road_dict[RSU]["MSI"][j+1]["Carriageway"] = "1"
            road_dict[RSU]["MSI"][j+1]["TrafficStream"] = "1"
            road_dict[RSU]["MSI"][j+1]["TrafficStream_Influence"]["Right"] = 20

  return road_dict




dataset = createDataSet(n_rsu,n_msi)

with open(data_file, "w") as outfile:
    json.dump(dataset, outfile) 