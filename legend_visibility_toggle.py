import xml.etree.ElementTree as ET


def toggle_visibility(svg_file, group_visibility):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    for group_id, visible in group_visibility.items():
        # Find the group element with the specified ID
        group = root.find(".//*[@id='{}']".format(group_id))

        if group is not None:
            group.attrib["visibility"] = "visible" if visible else "hidden"

    # Specify that namespaces (ns0) should not be written out
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree.write(svg_file, xml_declaration=True, method='xml', encoding='utf-8')


def translate_jvm_to_mtm(name_jvm: str) -> str:
    name_jvm = name_jvm[1:-1]  # Gets rid of leading and trailing [brackets]
    rsu, wegnummer, rijrichting_or_hecto, km_msi_nr = name_jvm.split("_")
    km, msi_nr = km_msi_nr.split(",")
    if rijrichting_or_hecto in ["L", "R"]:
        return f"{wegnummer}{rijrichting_or_hecto}:{km}:{msi_nr}"
    else:
        return f"{wegnummer}_{rijrichting_or_hecto}:{km}:{msi_nr}"


def determine_group_names(name_to_legend: dict) -> list:
    group_names = []
    for jvm_name, legend_list in name_to_legend.items():
        mtm_name = translate_jvm_to_mtm(jvm_name)
        for legend_name in legend_list:
            group_names.append(f"{legend_name}[{mtm_name}]")
    return group_names


svg_file = 'Server/Data/WEGGEG/road_visualization.svg'


# MSI images [for Vught example]
id_to_image = {'[RSU_A2_R_118.395,1]': ['i'], '[RSU_A2_R_118.395,2]': ['i'], '[RSU_A2_R_118.395,3]': ['i'], '[RSU_A2_R_118.395,4]': ['i'], '[RSU_A2_R_119.204,1]': ['g'], '[RSU_A2_R_119.204,2]': ['g'], '[RSU_A2_R_119.204,3]': ['l', 'a'], '[RSU_A2_R_119.204,4]': ['x'], '[RSU_A2_R_119.204,5]': ['x'], '[RSU_A2_R_119.47,1]': ['g'], '[RSU_A2_R_119.47,2]': ['g'], '[RSU_A2_R_119.47,3]': ['x'], '[RSU_A2_R_119.47,4]': ['x'], '[RSU_A2_R_119.47,5]': ['x'], '[RSU_A2_R_119.844,1]': ['z'], '[RSU_A2_R_119.844,2]': ['z'], '[RSU_A2_R_119.844,3]': ['z'], '[RSU_A2_R_119.844,4]': ['z'], '[RSU_A2_R_119.844,5]': ['z'], '[RSU_A2_A_118.72,1]': ['z'], '[RSU_A2_R_118.74,1]': ['i'], '[RSU_A2_R_118.74,2]': ['i'], '[RSU_A2_R_118.74,3]': ['i'], '[RSU_A2_R_118.74,4]': ['l', 'a']}
legends_to_activate = {name: True for name in determine_group_names(id_to_image)}

# group_visibility = {
#     'h[A58R:38.839:1]': True,
#     'h[A58R:38.839:2]': True,
#     'x[A58R:38.839:3]': True,
# }
toggle_visibility(svg_file, legends_to_activate)

