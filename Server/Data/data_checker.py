import json

data_file = "../../output_data.json"
# data_file = "a16_a58/data_a16_a58.json"
log_file = "log.txt"
only_composite_relations = False

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


def getRelations(road_layout, msirow, msi_nr, relation_type):
    [type_1, type_2] = relation_type.split("_")

    temp = road_layout[msirow]["MSI"][msi_nr][type_1][type_2]
    if temp:
        if isinstance(temp, list):
            temp = temp[0]
        return f"({msirow}:{msi_nr}, {temp})   {type_1} {type_2}"
    return None


with open(data_file) as json_file:
    road_layout = json.load(json_file)

source_file = open(log_file, 'w')
for i in relation_type:
    for msirow in road_layout:
        for msi_nr in road_layout[msirow]["MSI"]:
            relations = getRelations(road_layout, msirow, msi_nr, i)
            if relations:
                print(relations, file=source_file)
source_file.close

