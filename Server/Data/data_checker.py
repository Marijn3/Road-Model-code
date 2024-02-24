import json

data_file = "../../output_data.json"
data_file = "a16_a58/data_a16_a58.json"
log_file = "log.txt"
only_composite_relations = True

if not only_composite_relations:
    relation_type = [
        "Downstream_Primary",
        "Downstream_Secondary",
        "Downstream_Taper",
        "Downstream_Broadening",
        "Downstream_Narrowing",
        "Upstream_Primary",
        "Upstream_Secondary",
        "Upstream_Taper",
        "Upstream_Broadening",
        "Upstream_Narrowing"
    ]
if only_composite_relations:
    relation_type = [
        "Downstream_Secondary",
        "Downstream_Taper",
        "Downstream_Broadening",
        "Downstream_Narrowing",
        "Upstream_Secondary",
        "Upstream_Taper",
        "Upstream_Broadening",
        "Upstream_Narrowing"
    ]


def getRelations(road_layout, RSU, MSI, relation_type):
    [type_1, type_2] = relation_type.split("_")

    temp = road_layout[RSU]["MSI"][MSI][type_1][type_2]
    if temp:
        [RSU_2,MSI_2] = temp.split(",")
        return f"({RSU}_{MSI}, {RSU_2[1:]}_{MSI_2[:-1]})   {type_1} {type_2}"
    else:
        return None


with open(data_file) as json_file:
    road_layout = json.load(json_file)

source_file = open(log_file, 'w')
for i in relation_type:
    for RSU in road_layout:
        for MSI in road_layout[RSU]["MSI"]:
            relations = getRelations(road_layout, RSU, MSI, i)
            if relations:
                print(relations, file=source_file)
source_file.close

