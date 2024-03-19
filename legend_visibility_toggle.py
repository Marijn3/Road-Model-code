import xml.etree.ElementTree as ET


def toggle_visibility(svg_file, group_id, visible):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Find the group element with the specified ID
    group = root.find(".//*[@id='{}']".format(group_id))

    if group is not None:
        group.attrib["visibility"] = "visible" if visible else "hidden"
        # Specify that namespaces (ns0) should not be written out
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        tree.write(svg_file, xml_declaration=True, method='xml', encoding='utf-8')


svg_file = 'Server/Data/WEGGEG/road_visualization.svg'
group_id = 'z[A58L:38.839:2]'
visible = True
toggle_visibility(svg_file, group_id, visible)
