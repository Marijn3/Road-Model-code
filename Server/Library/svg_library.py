import xml.etree.ElementTree as ET

DEFS_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>

<svg
   width="750"
   height="750"
   viewBox="-30 0 720 750"
   version="1.1"
   id="svg5"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  
   <defs>
      <rect id="template_name_sign"
            style="fill:white;stroke:black;stroke-width:1"
            transform="translate(-1,-8)"
            width="43"
            height="10.5"/>
      <rect id="template_name_sign_wide"
            style="fill:white;stroke:black;stroke-width:1"
            transform="translate(-1,-8)"
            width="48"
            height="10.5"/>
            
      <rect id="template_legend_blank"
         style="fill:#afafaf;fill-opacity:1;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:0.5px"
         width="15"
         height="15"
         x="0"
         y="0" />   

      <text
         id="template_text_30"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">30</text>   
 
      <text
         id="template_text_40"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">40</text>   
               
      <text
         id="template_text_50"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">50</text>   
               
      <text
         id="template_text_60"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">60</text>   
               
      <text
         id="template_text_70"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">70</text>   
               
      <text
         id="template_text_80"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">80</text>   
               
      <text
         id="template_text_90"
         style="font-size:8px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">90</text>   
               
      <text
         id="template_text_100"
         style="font-size:6.35px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">100</text>   
               
      <text
         id="template_text_110"
         style="font-size:6.35px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">110</text>   
               
      <text
         id="template_text_120"
         style="font-size:6.35px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">120</text>   
                             
      <text
         id="template_text_130"
         style="font-size:6.35px;line-height:1.25;font-family:sans-serif"
         x="7.5"
         y="8.25"
         dominant-baseline="middle" 
         text-anchor="middle">130</text>   

      <g id="template_arrow">
         <path
            style="fill:none;stroke-width:0.79375;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
            d="m 4.5,4.5 4,4" />
         <path
            style="fill:none;stroke-width:0.79375;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
            d="m 10,5.5 v 4.5"
               />
         <path
            style="fill:none;stroke-width:0.79375;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
            d="m 5.5,10 h 4.5"
               />
      </g>

      <circle
            id="template_red_ring"
            style="fill:none;stroke:#b50000;stroke-width:0.657749;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
            cx="7.5"
            cy="7.5"
            r="6" />
      
      <circle
            style="fill:#ffdb24;fill-opacity:1;stroke:none;stroke-width:0.729001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1"
            id="template_flasher"
            cx="0"
            cy="0"
            r="1" />

      <g id="template_flashers">
         <use href="#template_flasher" x="2" y="2"/>
         <use href="#template_flasher" x="2" y="13"/>
         <use href="#template_flasher" x="13" y="2"/>
         <use href="#template_flasher" x="13" y="13"/>
      </g>

      <g
         id="legend_template_speed_30">
         <use href="#template_text_30" />
      </g>

      <g
         id="legend_template_speed_40">
         <use href="#template_text_40" />
      </g>

      <g
         id="legend_template_speed_50">
         <use href="#template_text_50" />
      </g>

      <g
         id="legend_template_speed_60">
         <use href="#template_text_60" />
      </g>

      <g
         id="legend_template_speed_70">
         <use href="#template_text_70" />
      </g>

      <g
         id="legend_template_speed_80">
         <use href="#template_text_80" />
      </g>

      <g
         id="legend_template_speed_90">
         <use href="#template_text_90" />
      </g>

      <g
         id="legend_template_speed_100">
         <use href="#template_text_100" />
      </g>

      <g
         id="legend_template_speed_110">
         <use href="#template_text_110" />
      </g>

      <g
         id="legend_template_speed_120">
         <use href="#template_text_120" />
      </g>

      <g
         id="legend_template_speed_130">
         <use href="#template_text_130" />
      </g>
 
      <g id="legend_template_right_arrow">
         <use href="#template_arrow" stroke="black"/>
      </g>
      
      <g id="legend_template_left_arrow">
         <use href="#template_arrow" transform="scale(-1,1),translate(-15,0)" stroke="black"/>
      </g>


      <g id="legend_template_green_arrow">
         <use href="#template_arrow" transform="rotate(45,7.5,7.5)" stroke="green"/>
      </g>

      <g id="legend_template_cross">
         <g style="stroke:#b50000;stroke-width:1;stroke-opacity:1">
            <path d="m 4.5,4.5 6,6"/>
            <path d="m 4.5,10.5 6,-6"/>
         </g>
      </g>

      <g id="legend_template_end_of_restrictions">
         <g style="fill:none;stroke:#000000;stroke-width:1;stroke-opacity:1">
            <circle 
               cx="7.5"
               cy="7.5"
               r="6"/>
            <path d="m 4.4,12.1 8,-8" stroke-width="0.6"/>
            <path d="m 2.9,10.6 8,-8" stroke-width="0.6"/>
         </g>
      </g>

   </defs> 

{content}
</svg>'''

USE_TEMPATE = '''<use href="#{legend_id}"/>'''


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


def toggle_visibility(svg_file, groups_to_activate):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    for group in root.findall(".//{http://www.w3.org/2000/svg}g"):
        group_id = group.attrib.get("id")

        if group_id is not None:
            if group_id in groups_to_activate:
                group.attrib["visibility"] = "visible"
            elif group_id[-1] == "]":
                # If the group ID is not in groups_to_activate, but contains a legend, default to hidden
                group.attrib["visibility"] = "hidden"

    # Specify that namespaces (ns0) should not be written out in the svg file
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree.write(svg_file, xml_declaration=True, method='xml', encoding='utf-8')


def createSVG_roadmodel(model, json_data):
    results, json_data = getMyVars(model, json_data)
    svg_file = "Server/Data/RoadModel/RoadModelVisualisation.svg"

    id_to_image = {key: value["State"] for key, value in json_data.items()}
    # print("New legends:", id_to_image)
    legends_to_activate = [name for name in determine_group_names(id_to_image)]
    toggle_visibility(svg_file, legends_to_activate)

    with open(svg_file, "r") as file:
        svg = file.read()

    return svg, json_data


def getMyVars(model, json_data):
    # couple model variables to svg variables
    legend_ids = {
        "x": 'legend_template_cross',
        "r": 'legend_template_right_arrow',
        "l": 'legend_template_left_arrow',
        "o": 'template_legend_blank',
        "e": 'legend_template_speed_50',
        "g": 'legend_template_speed_70',
        "h": 'legend_template_speed_80',
        "i": 'legend_template_speed_90',
        "j": 'legend_template_speed_100',
        "k": '',
        "y": 'legend_template_green_arrow',
        "z": 'legend_template_end_of_restrictions',
        "a": 'template_flashers',
        "b": 'template_red_ring'
    }

    # Create empty results set
    results = {}

    # Fill the results set with an empty list per MSI
    for MSI in json_data:
        results[MSI] = []

    # Fill the results with legend_ids that are active.
    for v in model.getVars():
        varname = v.getAttr('VarName')
        varval = v.getAttr('X')

        # Variable equal to 1 or 0, to avoid numerical errors no 'varval == 1' is used
        # Indicator variables should not be taken into account
        if (varval > 0.5) and (varname[1] == "_" or varname[1] == "["):
            split_varname = varname.split('[')
            legend = split_varname[0][0]
            key = f"[{split_varname[1]}"

            # make sure that RHL variables are used on every MSI of the respective RHL

            if json_data[key]['State'][0] == "Blank":
                json_data[key]['State'] = [legend]
            else:
                json_data[key]['State'].append(legend)

            results[key].append(
                USE_TEMPATE.format(
                    legend_id="".join(legend_ids[legend])))

    return results, json_data
