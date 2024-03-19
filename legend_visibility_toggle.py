import xml.etree.ElementTree as ET


def toggle_visibility(svg_file, group_id, visible):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Find the group element with the specified ID
    group = root.find(".//*[@id='{}']".format(group_id))

    # Update the visibility attribute
    if group is not None:
        group.attrib['style'] = 'visibility: {};'.format('visible' if visible else 'hidden')
        tree.write(svg_file)


# Example usage
svg_file = 'Server/Data/WEGGEG/road_visualization.svg'
group_id = 'r[A58L:38.839:2]'
visible = False  # Set visibility to False to hide the group
toggle_visibility(svg_file, group_id, visible)
