from Data.A15_Tunnel.svg_A15_tunnel import *
from Data.A50_Apeldoorn_Arnhem.svg_A50 import *
from Data.Klaverblad_A15_A27.svg_A15_A27 import *
from Data.Large_road.svg_eight_lane import *
from Data.Presentatie.svg_presentatie import *
from Data.a16_a58.svg_A16_A58 import *
from Data.circle.svg_circle import *
from Data.demo.svg_four_lane import *
from Data.demo2.svg_four_lane import *
from Data.large_road_2.svg_eight_lane import *
from Data.test.svg_test import *
from Data.test_RHL.svg_test_RHL import *

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


def createSVG_Presentatie(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_PRESENTATIE.format(
        RSU_A14_R_57_0_MSI_1="".join(results["[RSU_A14_R_57.0,1]"]),
        RSU_A14_R_57_0_MSI_2="".join(results["[RSU_A14_R_57.0,2]"]),
        RSU_A14_R_58_0_MSI_1="".join(results["[RSU_A14_R_58.0,1]"]),
        RSU_A14_R_58_0_MSI_2="".join(results["[RSU_A14_R_58.0,2]"]),
        RSU_A3_r_2_9_MSI_1="".join(results["[RSU_A3_r_2.9,1]"]),
        RSU_A3_R_0_0_MSI_1="".join(results["[RSU_A3_R_0.0,1]"]),
        RSU_A3_R_0_0_MSI_2="".join(results["[RSU_A3_R_0.0,2]"]),
        RSU_A3_R_1_0_MSI_1="".join(results["[RSU_A3_R_1.0,1]"]),
        RSU_A3_R_1_0_MSI_2="".join(results["[RSU_A3_R_1.0,2]"]),
        RSU_A3_R_2_0_MSI_1="".join(results["[RSU_A3_R_2.0,1]"]),
        RSU_A3_R_2_0_MSI_2="".join(results["[RSU_A3_R_2.0,2]"]),
        RSU_A3_R_2_0_MSI_3="".join(results["[RSU_A3_R_2.0,3]"]),
        RSU_A3_R_3_0_MSI_1="".join(results["[RSU_A3_R_3.0,1]"]),
        RSU_A3_R_3_0_MSI_2="".join(results["[RSU_A3_R_3.0,2]"]),
        RSU_A3_R_3_0_MSI_3="".join(results["[RSU_A3_R_3.0,3]"]),
        RSU_A3_R_4_0_MSI_1="".join(results["[RSU_A3_R_4.0,1]"]),
        RSU_A3_R_4_0_MSI_2="".join(results["[RSU_A3_R_4.0,2]"]),
        RSU_A3_R_4_0_MSI_3="".join(results["[RSU_A3_R_4.0,3]"]),
        RSU_A3_R_5_0_MSI_1="".join(results["[RSU_A3_R_5.0,1]"]),
        RSU_A3_R_5_0_MSI_2="".join(results["[RSU_A3_R_5.0,2]"]),
    )

    empty_road = EMPTY_ROAD_TEMPLATE_PRESENTATIE.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_test(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_TEST.format(
        RSU1_MSI1="".join(results["[RSU_A684_R_65_5,1]"]),
        RSU2_MSI1="".join(results["[RSU_A684_R_66_2,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_R_66_2,2]"]),
        RSU3_MSI1="".join(results["[RSU_A684_R_66_8,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_R_66_8,2]"]),
        RSU4_MSI1="".join(results["[RSU_A684_R_67_5,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_R_67_5,2]"]),
    )

    empty_road = EMPTY_ROAD_TEMPLATE_TEST.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_roadmodel(model, json_data):
    results, json_data = getMyVars(model, json_data)
    with open("Server/Data/WEGGEG/road_visualization.svg", "r") as file:
        svg = file.read()
    return svg, json_data


def createSVG_A16_A58(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_A16_A58.format(
        RSU_A16_R_65_5_MSI1="".join(results["[RSU_A16_R_65.5,1]"]),
        RSU_A16_R_65_5_MSI2="".join(results["[RSU_A16_R_65.5,2]"]),
        RSU_A16_R_65_5_MSI3="".join(results["[RSU_A16_R_65.5,3]"]),
        RSU_A16_R_66_2_MSI1="".join(results["[RSU_A16_R_66.2,1]"]),
        RSU_A16_R_66_2_MSI2="".join(results["[RSU_A16_R_66.2,2]"]),
        RSU_A16_R_66_2_MSI3="".join(results["[RSU_A16_R_66.2,3]"]),
        RSU_A16_R_66_6_MSI1="".join(results["[RSU_A16_R_66.6,1]"]),
        RSU_A16_R_66_6_MSI2="".join(results["[RSU_A16_R_66.6,2]"]),
        RSU_A16_R_66_6_MSI3="".join(results["[RSU_A16_R_66.6,3]"]),
        RSU_A16_R_66_6_MSI4="".join(results["[RSU_A16_R_66.6,4]"]),
        RSU_A16_R_66_8_MSI1="".join(results["[RSU_A16_R_66.8,1]"]),
        RSU_A16_R_66_8_MSI2="".join(results["[RSU_A16_R_66.8,2]"]),
        RSU_A16_R_66_8_MSI3="".join(results["[RSU_A16_R_66.8,3]"]),
        RSU_A16_R_66_8_MSI4="".join(results["[RSU_A16_R_66.8,4]"]),
        RSU_A16_R_67_6_MSI1="".join(results["[RSU_A16_R_67.6,1]"]),
        RSU_A16_R_67_6_MSI2="".join(results["[RSU_A16_R_67.6,2]"]),
        RSU_A16_R_68_5_MSI1="".join(results["[RSU_A16_R_68.5,1]"]),
        RSU_A16_R_68_5_MSI2="".join(results["[RSU_A16_R_68.5,2]"]),
        RSU_A16_L_65_5_MSI1="".join(results["[RSU_A16_L_65.5,1]"]),
        RSU_A16_L_65_5_MSI2="".join(results["[RSU_A16_L_65.5,2]"]),
        RSU_A16_L_65_5_MSI3="".join(results["[RSU_A16_L_65.5,3]"]),
        RSU_A16_L_66_2_MSI1="".join(results["[RSU_A16_L_66.2,1]"]),
        RSU_A16_L_66_2_MSI2="".join(results["[RSU_A16_L_66.2,2]"]),
        RSU_A16_L_66_2_MSI3="".join(results["[RSU_A16_L_66.2,3]"]),
        RSU_A16_L_66_8_MSI1="".join(results["[RSU_A16_L_66.8,1]"]),
        RSU_A16_L_66_8_MSI2="".join(results["[RSU_A16_L_66.8,2]"]),
        RSU_A16_L_66_8_MSI3="".join(results["[RSU_A16_L_66.8,3]"]),
        RSU_A16_L_67_8_MSI1="".join(results["[RSU_A16_L_67.8,1]"]),
        RSU_A16_L_67_8_MSI2="".join(results["[RSU_A16_L_67.8,2]"]),
        RSU_A16_L_68_5_MSI1="".join(results["[RSU_A16_L_68.5,1]"]),
        RSU_A16_L_68_5_MSI2="".join(results["[RSU_A16_L_68.5,2]"]),
        RSU_A16_L_68_5_MSI3="".join(results["[RSU_A16_L_68.5,3]"]),
        RSU_A58_R_62_1_MSI1="".join(results["[RSU_A58_R_62.1,1]"]),
        RSU_A58_R_62_1_MSI2="".join(results["[RSU_A58_R_62.1,2]"]),
        RSU_A58_R_62_1_MSI3="".join(results["[RSU_A58_R_62.1,3]"]),
        RSU_A58_R_61_8_MSI1="".join(results["[RSU_A58_R_61.8,1]"]),
        RSU_A58_R_61_8_MSI2="".join(results["[RSU_A58_R_61.8,2]"]),
        RSU_A58_R_61_8_MSI3="".join(results["[RSU_A58_R_61.8,3]"]),
        RSU_A58_R_61_2_MSI1="".join(results["[RSU_A58_R_61.2,1]"]),
        RSU_A58_R_61_2_MSI2="".join(results["[RSU_A58_R_61.2,2]"]),
        RSU_A58_R_61_2_MSI3="".join(results["[RSU_A58_R_61.2,3]"]),
        RSU_A58_R_60_6_MSI1="".join(results["[RSU_A58_R_60.6,1]"]),
        RSU_A58_R_60_6_MSI2="".join(results["[RSU_A58_R_60.6,2]"]),
        RSU_A58_R_60_1_MSI1="".join(results["[RSU_A58_R_60.1,1]"]),
        RSU_A58_R_60_1_MSI2="".join(results["[RSU_A58_R_60.1,2]"]),
        RSU_A58_L_61_9_MSI1="".join(results["[RSU_A58_L_61.9,1]"]),
        RSU_A58_L_61_9_MSI2="".join(results["[RSU_A58_L_61.9,2]"]),
        RSU_A58_L_61_9_MSI3="".join(results["[RSU_A58_L_61.9,3]"]),
        RSU_A58_L_61_2_MSI1="".join(results["[RSU_A58_L_61.2,1]"]),
        RSU_A58_L_61_2_MSI2="".join(results["[RSU_A58_L_61.2,2]"]),
        RSU_A58_L_61_2_MSI3="".join(results["[RSU_A58_L_61.2,3]"]),
        RSU_A58_L_60_6_MSI1="".join(results["[RSU_A58_L_60.6,1]"]),
        RSU_A58_L_60_6_MSI2="".join(results["[RSU_A58_L_60.6,2]"]),
        RSU_A58_L_60_1_MSI1="".join(results["[RSU_A58_L_60.1,1]"]),
        RSU_A58_L_60_1_MSI2="".join(results["[RSU_A58_L_60.1,2]"]),
        RSU_A58_L_62_7_MSI1="".join(results["[RSU_A58_L_62.7,1]"]),
        RSU_A58_L_62_7_MSI2="".join(results["[RSU_A58_L_62.7,2]"]),
        RSU_A16_R_67_4g_MSI1="".join(results["[RSU_A16_R_67.4g,1]"]),
        RSU_A16_R_67_4g_MSI2="".join(results["[RSU_A16_R_67.4g,2]"]),
        RSU_A58_R_62_7r_MSI1="".join(results["[RSU_A58_R_62.7r,1]"]),
        RSU_A58_R_62_7r_MSI2="".join(results["[RSU_A58_R_62.7r,2]"]),
        RSU_A58_R_62_7_MSI1="".join(results["[RSU_A58_R_62.7,1]"]),
        RSU_A16_L_67_9f_MSI1="".join(results["[RSU_A16_L_67.9f,1]"]),
    )

    empty_road = EMPTY_ROAD_TEMPLATE_A16_A58.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_test_RHL(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_TEST_RHL.format(
        RSU1_MSI1="".join(results["[RSU_A684_R_65_5,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_R_65_5,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_R_65_5,3]"]),

        RSU2_MSI1="".join(results["[RSU_A684_R_66_2,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_R_66_2,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_R_66_2,3]"]),

        RSU3_MSI1="".join(results["[RSU_A684_R_66_8,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_R_66_8,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_R_66_8,3]"]),

        RSU4_MSI1="".join(results["[RSU_A684_R_67_5,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_R_67_5,2]"]),
        # RSU4_MSI3="".join(results["[RSU_A684_R_67_5,3]"]),
        RSU4_MSI3=""
    )

    empty_road = EMPTY_ROAD_TEMPLATE_TEST_RHL.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Klaverblad_A15_A27(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_A15_A27.format(
        RSU_A15_L_93_810_MSI_1="".join(results["[RSU_A15_L_93.810,1]"]),
        RSU_A15_L_93_810_MSI_2="".join(results["[RSU_A15_L_93.810,2]"]),
        RSU_A15_L_94_270_MSI_1="".join(results["[RSU_A15_L_94.270,1]"]),
        RSU_A15_L_94_270_MSI_2="".join(results["[RSU_A15_L_94.270,2]"]),
        RSU_A15_L_94_625_MSI_1="".join(results["[RSU_A15_L_94.625,1]"]),
        RSU_A15_L_94_625_MSI_2="".join(results["[RSU_A15_L_94.625,2]"]),
        RSU_A15_L_95_190_MSI_1="".join(results["[RSU_A15_L_95.190,1]"]),
        RSU_A15_L_95_190_MSI_2="".join(results["[RSU_A15_L_95.190,2]"]),
        RSU_A15_L_95_550_MSI_1="".join(results["[RSU_A15_L_95.550,1]"]),
        RSU_A15_L_95_550_MSI_2="".join(results["[RSU_A15_L_95.550,2]"]),
        RSU_A15_L_95_855_MSI_1="".join(results["[RSU_A15_L_95.855,1]"]),
        RSU_A15_L_95_855_MSI_2="".join(results["[RSU_A15_L_95.855,2]"]),
        RSU_A15_L_96_260_MSI_1="".join(results["[RSU_A15_L_96.260,1]"]),
        RSU_A15_L_96_260_MSI_2="".join(results["[RSU_A15_L_96.260,2]"]),
        RSU_A15_L_96_855_MSI_1="".join(results["[RSU_A15_L_96.855,1]"]),
        RSU_A15_L_96_855_MSI_2="".join(results["[RSU_A15_L_96.855,2]"]),
        RSU_A15_L_97_200_MSI_1="".join(results["[RSU_A15_L_97.200,1]"]),
        RSU_A15_L_97_200_MSI_2="".join(results["[RSU_A15_L_97.200,2]"]),
        RSU_A15_L_97_660_MSI_1="".join(results["[RSU_A15_L_97.660,1]"]),
        RSU_A15_L_97_660_MSI_2="".join(results["[RSU_A15_L_97.660,2]"]),
        RSU_A15_L_98_165_MSI_1="".join(results["[RSU_A15_L_98.165,1]"]),
        RSU_A15_L_98_165_MSI_2="".join(results["[RSU_A15_L_98.165,2]"]),
        RSU_A15_L_98_600_MSI_1="".join(results["[RSU_A15_L_98.600,1]"]),
        RSU_A15_L_98_600_MSI_2="".join(results["[RSU_A15_L_98.600,2]"]),
        RSU_A15_L_99_050_MSI_1="".join(results["[RSU_A15_L_99.050,1]"]),
        RSU_A15_L_99_050_MSI_2="".join(results["[RSU_A15_L_99.050,2]"]),
        RSU_A15_L_99_500_MSI_1="".join(results["[RSU_A15_L_99.500,1]"]),
        RSU_A15_L_99_500_MSI_2="".join(results["[RSU_A15_L_99.500,2]"]),
        RSU_A15_L_100_000_MSI_1="".join(results["[RSU_A15_L_100.000,1]"]),
        RSU_A15_L_100_000_MSI_2="".join(results["[RSU_A15_L_100.000,2]"]),
        RSU_A15_L_100_600_MSI_1="".join(results["[RSU_A15_L_100.600,1]"]),
        RSU_A15_L_100_600_MSI_2="".join(results["[RSU_A15_L_100.600,2]"]),
        RSU_A15_L_101_200_MSI_1="".join(results["[RSU_A15_L_101.200,1]"]),
        RSU_A15_L_101_200_MSI_2="".join(results["[RSU_A15_L_101.200,2]"]),
        RSU_A15_f_96_000_MSI_1="".join(results["[RSU_A15_f_96.000,1]"]),
        RSU_A15_n_94_625_MSI_1="".join(results["[RSU_A15_n_94.625,1]"]),
        RSU_A15_n_95_285_MSI_1="".join(results["[RSU_A15_n_95.285,1]"]),
        RSU_A15_n_95_285_MSI_2="".join(results["[RSU_A15_n_95.285,2]"]),
        RSU_A15_n_95_285_MSI_3="".join(results["[RSU_A15_n_95.285,3]"]),
        RSU_A15_n_95_855_MSI_1="".join(results["[RSU_A15_n_95.855,1]"]),
        RSU_A15_n_95_855_MSI_2="".join(results["[RSU_A15_n_95.855,2]"]),
        RSU_A15_n_95_855_MSI_3="".join(results["[RSU_A15_n_95.855,3]"]),
        RSU_A15_n_96_420_MSI_1="".join(results["[RSU_A15_n_96.420,1]"]),
        RSU_A15_n_96_420_MSI_2="".join(results["[RSU_A15_n_96.420,2]"]),
        RSU_A15_n_96_420_MSI_3="".join(results["[RSU_A15_n_96.420,3]"]),
        RSU_A15_n_96_820_MSI_1="".join(results["[RSU_A15_n_96.820,1]"]),
        RSU_A15_n_96_820_MSI_2="".join(results["[RSU_A15_n_96.820,2]"]),
        RSU_A15_R_93_810_MSI_1="".join(results["[RSU_A15_R_93.810,1]"]),
        RSU_A15_R_93_810_MSI_2="".join(results["[RSU_A15_R_93.810,2]"]),
        RSU_A15_R_94_270_MSI_1="".join(results["[RSU_A15_R_94.270,1]"]),
        RSU_A15_R_94_270_MSI_2="".join(results["[RSU_A15_R_94.270,2]"]),
        RSU_A15_R_94_270_MSI_3="".join(results["[RSU_A15_R_94.270,3]"]),
        RSU_A15_R_94_490_MSI_1="".join(results["[RSU_A15_R_94.490,1]"]),
        RSU_A15_R_94_490_MSI_2="".join(results["[RSU_A15_R_94.490,2]"]),
        RSU_A15_R_94_725_MSI_1="".join(results["[RSU_A15_R_94.725,1]"]),
        RSU_A15_R_94_725_MSI_2="".join(results["[RSU_A15_R_94.725,2]"]),
        RSU_A15_R_95_190_MSI_1="".join(results["[RSU_A15_R_95.190,1]"]),
        RSU_A15_R_95_190_MSI_2="".join(results["[RSU_A15_R_95.190,2]"]),
        RSU_A15_R_95_760_MSI_1="".join(results["[RSU_A15_R_95.760,1]"]),
        RSU_A15_R_95_760_MSI_2="".join(results["[RSU_A15_R_95.760,2]"]),
        RSU_A15_R_96_260_MSI_1="".join(results["[RSU_A15_R_96.260,1]"]),
        RSU_A15_R_96_260_MSI_2="".join(results["[RSU_A15_R_96.260,2]"]),
        RSU_A15_R_96_680_MSI_1="".join(results["[RSU_A15_R_96.680,1]"]),
        RSU_A15_R_96_680_MSI_2="".join(results["[RSU_A15_R_96.680,2]"]),
        RSU_A15_R_97_200_MSI_1="".join(results["[RSU_A15_R_97.200,1]"]),
        RSU_A15_R_97_200_MSI_2="".join(results["[RSU_A15_R_97.200,2]"]),
        RSU_A15_R_97_660_MSI_1="".join(results["[RSU_A15_R_97.660,1]"]),
        RSU_A15_R_97_660_MSI_2="".join(results["[RSU_A15_R_97.660,2]"]),
        RSU_A15_R_98_165_MSI_1="".join(results["[RSU_A15_R_98.165,1]"]),
        RSU_A15_R_98_165_MSI_2="".join(results["[RSU_A15_R_98.165,2]"]),
        RSU_A15_R_98_600_MSI_1="".join(results["[RSU_A15_R_98.600,1]"]),
        RSU_A15_R_98_600_MSI_2="".join(results["[RSU_A15_R_98.600,2]"]),
        RSU_A15_R_99_050_MSI_1="".join(results["[RSU_A15_R_99.050,1]"]),
        RSU_A15_R_99_050_MSI_2="".join(results["[RSU_A15_R_99.050,2]"]),
        RSU_A15_R_99_350_MSI_1="".join(results["[RSU_A15_R_99.350,1]"]),
        RSU_A15_R_99_350_MSI_2="".join(results["[RSU_A15_R_99.350,2]"]),
        RSU_A15_R_99_350_MSI_3="".join(results["[RSU_A15_R_99.350,3]"]),
        RSU_A15_R_100_000_MSI_1="".join(results["[RSU_A15_R_100.000,1]"]),
        RSU_A15_R_100_000_MSI_2="".join(results["[RSU_A15_R_100.000,2]"]),
        RSU_A15_R_100_600_MSI_1="".join(results["[RSU_A15_R_100.600,1]"]),
        RSU_A15_R_100_600_MSI_2="".join(results["[RSU_A15_R_100.600,2]"]),
        RSU_A15_R_101_200_MSI_1="".join(results["[RSU_A15_R_101.200,1]"]),
        RSU_A15_R_101_200_MSI_2="".join(results["[RSU_A15_R_101.200,2]"]),
        RSU_A15_e_95_550_MSI_1="".join(results["[RSU_A15_e_95.550,1]"]),
        RSU_A15_m_94_500_MSI_1="".join(results["[RSU_A15_m_94.500,1]"]),
        RSU_A15_m_94_500_MSI_2="".join(results["[RSU_A15_m_94.500,2]"]),
        RSU_A15_m_94_725_MSI_1="".join(results["[RSU_A15_m_94.725,1]"]),
        RSU_A15_m_94_725_MSI_2="".join(results["[RSU_A15_m_94.725,2]"]),
        RSU_A15_m_94_725_MSI_3="".join(results["[RSU_A15_m_94.725,3]"]),
        RSU_A15_m_95_300_MSI_1="".join(results["[RSU_A15_m_95.300,1]"]),
        RSU_A15_m_95_300_MSI_2="".join(results["[RSU_A15_m_95.300,2]"]),
        RSU_A15_m_95_300_MSI_3="".join(results["[RSU_A15_m_95.300,3]"]),
        RSU_A15_m_95_760_MSI_1="".join(results["[RSU_A15_m_95.760,1]"]),
        RSU_A15_m_95_760_MSI_2="".join(results["[RSU_A15_m_95.760,2]"]),
        RSU_A15_m_95_760_MSI_3="".join(results["[RSU_A15_m_95.760,3]"]),
        RSU_A15_m_96_180_MSI_1="".join(results["[RSU_A15_m_96.180,1]"]),
        RSU_A15_m_96_180_MSI_2="".join(results["[RSU_A15_m_96.180,2]"]),
        RSU_A15_m_96_680_MSI_1="".join(results["[RSU_A15_m_96.680,1]"]),
        RSU_A27_L_34_665_MSI_1="".join(results["[RSU_A27_L_34.665,1]"]),
        RSU_A27_L_34_665_MSI_2="".join(results["[RSU_A27_L_34.665,2]"]),
        RSU_A27_L_35_110_MSI_1="".join(results["[RSU_A27_L_35.110,1]"]),
        RSU_A27_L_35_110_MSI_2="".join(results["[RSU_A27_L_35.110,2]"]),
        RSU_A27_L_35_410_MSI_1="".join(results["[RSU_A27_L_35.410,1]"]),
        RSU_A27_L_35_410_MSI_2="".join(results["[RSU_A27_L_35.410,2]"]),
        RSU_A27_L_35_690_MSI_1="".join(results["[RSU_A27_L_35.690,1]"]),
        RSU_A27_L_35_690_MSI_2="".join(results["[RSU_A27_L_35.690,2]"]),
        RSU_A27_L_35_690_MSI_3="".join(results["[RSU_A27_L_35.690,3]"]),
        RSU_A27_L_36_060_MSI_1="".join(results["[RSU_A27_L_36.060,1]"]),
        RSU_A27_L_36_060_MSI_2="".join(results["[RSU_A27_L_36.060,2]"]),
        RSU_A27_L_36_060_MSI_3="".join(results["[RSU_A27_L_36.060,3]"]),
        RSU_A27_L_36_550_MSI_1="".join(results["[RSU_A27_L_36.550,1]"]),
        RSU_A27_L_36_550_MSI_2="".join(results["[RSU_A27_L_36.550,2]"]),
        RSU_A27_L_37_115_MSI_1="".join(results["[RSU_A27_L_37.115,1]"]),
        RSU_A27_L_37_115_MSI_2="".join(results["[RSU_A27_L_37.115,2]"]),
        RSU_A27_L_37_630_MSI_1="".join(results["[RSU_A27_L_37.630,1]"]),
        RSU_A27_L_37_630_MSI_2="".join(results["[RSU_A27_L_37.630,2]"]),
        RSU_A27_L_37_630_MSI_3="".join(results["[RSU_A27_L_37.630,3]"]),
        RSU_A27_L_37_630_MSI_4="".join(results["[RSU_A27_L_37.630,4]"]),
        RSU_A27_L_38_080_MSI_1="".join(results["[RSU_A27_L_38.080,1]"]),
        RSU_A27_L_38_080_MSI_2="".join(results["[RSU_A27_L_38.080,2]"]),
        RSU_A27_L_38_080_MSI_3="".join(results["[RSU_A27_L_38.080,3]"]),
        RSU_A27_L_38_475_MSI_1="".join(results["[RSU_A27_L_38.475,1]"]),
        RSU_A27_L_38_475_MSI_2="".join(results["[RSU_A27_L_38.475,2]"]),
        RSU_A27_L_38_475_MSI_3="".join(results["[RSU_A27_L_38.475,3]"]),
        RSU_A27_L_38_850_MSI_1="".join(results["[RSU_A27_L_38.850,1]"]),
        RSU_A27_L_38_850_MSI_2="".join(results["[RSU_A27_L_38.850,2]"]),
        RSU_A27_L_38_850_MSI_3="".join(results["[RSU_A27_L_38.850,3]"]),
        RSU_A27_L_39_450_MSI_1="".join(results["[RSU_A27_L_39.450,1]"]),
        RSU_A27_L_39_450_MSI_2="".join(results["[RSU_A27_L_39.450,2]"]),
        RSU_A27_L_39_950_MSI_1="".join(results["[RSU_A27_L_39.950,1]"]),
        RSU_A27_L_39_950_MSI_2="".join(results["[RSU_A27_L_39.950,2]"]),
        RSU_A27_L_40_440_MSI_1="".join(results["[RSU_A27_L_40.440,1]"]),
        RSU_A27_L_40_440_MSI_2="".join(results["[RSU_A27_L_40.440,2]"]),
        RSU_A27_L_41_000_MSI_1="".join(results["[RSU_A27_L_41.000,1]"]),
        RSU_A27_L_41_000_MSI_2="".join(results["[RSU_A27_L_41.000,2]"]),
        RSU_A27_L_41_500_MSI_1="".join(results["[RSU_A27_L_41.500,1]"]),
        RSU_A27_L_41_500_MSI_2="".join(results["[RSU_A27_L_41.500,2]"]),
        RSU_A27_L_41_910_MSI_1="".join(results["[RSU_A27_L_41.910,1]"]),
        RSU_A27_L_41_910_MSI_2="".join(results["[RSU_A27_L_41.910,2]"]),
        RSU_A27_L_42_380_MSI_1="".join(results["[RSU_A27_L_42.380,1]"]),
        RSU_A27_L_42_380_MSI_2="".join(results["[RSU_A27_L_42.380,2]"]),
        RSU_A27_L_42_890_MSI_1="".join(results["[RSU_A27_L_42.890,1]"]),
        RSU_A27_L_42_890_MSI_2="".join(results["[RSU_A27_L_42.890,2]"]),
        RSU_A27_L_43_500_MSI_1="".join(results["[RSU_A27_L_43.500,1]"]),
        RSU_A27_L_43_500_MSI_2="".join(results["[RSU_A27_L_43.500,2]"]),
        RSU_A27_s_36_950_MSI_1="".join(results["[RSU_A27_s_36.950,1]"]),
        RSU_A27_y_36_720_MSI_1="".join(results["[RSU_A27_y_36.720,1]"]),
        RSU_A27_y_36_720_MSI_2="".join(results["[RSU_A27_y_36.720,2]"]),
        RSU_A27_y_37_300_MSI_1="".join(results["[RSU_A27_y_37.300,1]"]),
        RSU_A27_y_37_300_MSI_2="".join(results["[RSU_A27_y_37.300,2]"]),
        RSU_A27_R_34_665_MSI_1="".join(results["[RSU_A27_R_34.665,1]"]),
        RSU_A27_R_34_665_MSI_2="".join(results["[RSU_A27_R_34.665,2]"]),
        RSU_A27_R_35_110_MSI_1="".join(results["[RSU_A27_R_35.110,1]"]),
        RSU_A27_R_35_110_MSI_2="".join(results["[RSU_A27_R_35.110,2]"]),
        RSU_A27_R_35_380_MSI_1="".join(results["[RSU_A27_R_35.380,1]"]),
        RSU_A27_R_35_380_MSI_2="".join(results["[RSU_A27_R_35.380,2]"]),
        RSU_A27_R_35_690_MSI_1="".join(results["[RSU_A27_R_35.690,1]"]),
        RSU_A27_R_35_690_MSI_2="".join(results["[RSU_A27_R_35.690,2]"]),
        RSU_A27_R_35_690_MSI_3="".join(results["[RSU_A27_R_35.690,3]"]),
        RSU_A27_R_36_165_MSI_1="".join(results["[RSU_A27_R_36.165,1]"]),
        RSU_A27_R_36_165_MSI_2="".join(results["[RSU_A27_R_36.165,2]"]),
        RSU_A27_R_36_550_MSI_1="".join(results["[RSU_A27_R_36.550,1]"]),
        RSU_A27_R_36_550_MSI_2="".join(results["[RSU_A27_R_36.550,2]"]),
        RSU_A27_R_37_135_MSI_1="".join(results["[RSU_A27_R_37.135,1]"]),
        RSU_A27_R_37_135_MSI_2="".join(results["[RSU_A27_R_37.135,2]"]),
        RSU_A27_R_37_630_MSI_1="".join(results["[RSU_A27_R_37.630,1]"]),
        RSU_A27_R_37_630_MSI_2="".join(results["[RSU_A27_R_37.630,2]"]),
        RSU_A27_R_37_630_MSI_3="".join(results["[RSU_A27_R_37.630,3]"]),
        RSU_A27_R_37_630_MSI_4="".join(results["[RSU_A27_R_37.630,4]"]),
        RSU_A27_R_38_080_MSI_1="".join(results["[RSU_A27_R_38.080,1]"]),
        RSU_A27_R_38_080_MSI_2="".join(results["[RSU_A27_R_38.080,2]"]),
        RSU_A27_R_38_080_MSI_3="".join(results["[RSU_A27_R_38.080,3]"]),
        RSU_A27_R_38_475_MSI_1="".join(results["[RSU_A27_R_38.475,1]"]),
        RSU_A27_R_38_475_MSI_2="".join(results["[RSU_A27_R_38.475,2]"]),
        RSU_A27_R_38_475_MSI_3="".join(results["[RSU_A27_R_38.475,3]"]),
        RSU_A27_R_38_850_MSI_1="".join(results["[RSU_A27_R_38.850,1]"]),
        RSU_A27_R_38_850_MSI_2="".join(results["[RSU_A27_R_38.850,2]"]),
        RSU_A27_R_38_850_MSI_3="".join(results["[RSU_A27_R_38.850,3]"]),
        RSU_A27_R_39_450_MSI_1="".join(results["[RSU_A27_R_39.450,1]"]),
        RSU_A27_R_39_450_MSI_2="".join(results["[RSU_A27_R_39.450,2]"]),
        RSU_A27_R_39_450_MSI_3="".join(results["[RSU_A27_R_39.450,3]"]),
        RSU_A27_R_39_950_MSI_1="".join(results["[RSU_A27_R_39.950,1]"]),
        RSU_A27_R_39_950_MSI_2="".join(results["[RSU_A27_R_39.950,2]"]),
        RSU_A27_R_39_950_MSI_3="".join(results["[RSU_A27_R_39.950,3]"]),
        RSU_A27_R_40_440_MSI_1="".join(results["[RSU_A27_R_40.440,1]"]),
        RSU_A27_R_40_440_MSI_2="".join(results["[RSU_A27_R_40.440,2]"]),
        RSU_A27_R_40_440_MSI_3="".join(results["[RSU_A27_R_40.440,3]"]),
        RSU_A27_R_41_000_MSI_1="".join(results["[RSU_A27_R_41.000,1]"]),
        RSU_A27_R_41_000_MSI_2="".join(results["[RSU_A27_R_41.000,2]"]),
        RSU_A27_R_41_000_MSI_3="".join(results["[RSU_A27_R_41.000,3]"]),
        RSU_A27_R_41_500_MSI_1="".join(results["[RSU_A27_R_41.500,1]"]),
        RSU_A27_R_41_500_MSI_2="".join(results["[RSU_A27_R_41.500,2]"]),
        RSU_A27_R_41_500_MSI_3="".join(results["[RSU_A27_R_41.500,3]"]),
        RSU_A27_R_41_910_MSI_1="".join(results["[RSU_A27_R_41.910,1]"]),
        RSU_A27_R_41_910_MSI_2="".join(results["[RSU_A27_R_41.910,2]"]),
        RSU_A27_R_41_910_MSI_3="".join(results["[RSU_A27_R_41.910,3]"]),
        RSU_A27_R_42_380_MSI_1="".join(results["[RSU_A27_R_42.380,1]"]),
        RSU_A27_R_42_380_MSI_2="".join(results["[RSU_A27_R_42.380,2]"]),
        RSU_A27_R_42_380_MSI_3="".join(results["[RSU_A27_R_42.380,3]"]),
        RSU_A27_R_42_890_MSI_1="".join(results["[RSU_A27_R_42.890,1]"]),
        RSU_A27_R_42_890_MSI_2="".join(results["[RSU_A27_R_42.890,2]"]),
        RSU_A27_R_43_500_MSI_1="".join(results["[RSU_A27_R_43.500,1]"]),
        RSU_A27_R_43_500_MSI_2="".join(results["[RSU_A27_R_43.500,2]"]),
        RSU_A27_r_36_740_MSI_1="".join(results["[RSU_A27_r_36.740,1]"]),
        RSU_A27_r_36_990_MSI_1="".join(results["[RSU_A27_r_36.990,1]"]),
        RSU_A27_x_36_165_MSI_1="".join(results["[RSU_A27_x_36.165,1]"]),
        RSU_A27_x_36_165_MSI_2="".join(results["[RSU_A27_x_36.165,2]"]),
        RSU_A27_x_36_410_MSI_1="".join(results["[RSU_A27_x_36.410,1]"]),
        RSU_A27_x_36_410_MSI_2="".join(results["[RSU_A27_x_36.410,2]"]),
        RSU_A27_x_36_900_MSI_1="".join(results["[RSU_A27_x_36.900,1]"]),
        RSU_A27_x_36_900_MSI_2="".join(results["[RSU_A27_x_36.900,2]"]),
        RSU_A27_x_37_300_MSI_1="".join(results["[RSU_A27_x_37.300,1]"]),
        RSU_A27_x_37_300_MSI_2="".join(results["[RSU_A27_x_37.300,2]"])

    )

    empty_road = EMPTY_ROAD_TEMPLATE_A15_A27.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_A50(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_A50.format(
        RSU_A12_f_128_100_MSI_1="".join(results["[RSU_A12_f_128.100,1]"]),
        RSU_A50_L_182_890_MSI_1="".join(results["[RSU_A50_L_182.890,1]"]),
        RSU_A50_L_182_890_MSI_2="".join(results["[RSU_A50_L_182.890,2]"]),
        RSU_A50_L_183_375_MSI_1="".join(results["[RSU_A50_L_183.375,1]"]),
        RSU_A50_L_183_375_MSI_2="".join(results["[RSU_A50_L_183.375,2]"]),
        RSU_A50_L_183_375_MSI_3="".join(results["[RSU_A50_L_183.375,3]"]),
        RSU_A50_L_183_800_MSI_1="".join(results["[RSU_A50_L_183.800,1]"]),
        RSU_A50_L_183_800_MSI_2="".join(results["[RSU_A50_L_183.800,2]"]),
        RSU_A50_L_183_800_MSI_3="".join(results["[RSU_A50_L_183.800,3]"]),
        RSU_A50_L_184_200_MSI_1="".join(results["[RSU_A50_L_184.200,1]"]),
        RSU_A50_L_184_200_MSI_2="".join(results["[RSU_A50_L_184.200,2]"]),
        RSU_A50_L_184_200_MSI_3="".join(results["[RSU_A50_L_184.200,3]"]),
        RSU_A50_L_184_715_MSI_1="".join(results["[RSU_A50_L_184.715,1]"]),
        RSU_A50_L_184_715_MSI_2="".join(results["[RSU_A50_L_184.715,2]"]),
        RSU_A50_L_184_715_MSI_3="".join(results["[RSU_A50_L_184.715,3]"]),
        RSU_A50_L_185_205_MSI_1="".join(results["[RSU_A50_L_185.205,1]"]),
        RSU_A50_L_185_205_MSI_2="".join(results["[RSU_A50_L_185.205,2]"]),
        RSU_A50_L_185_205_MSI_3="".join(results["[RSU_A50_L_185.205,3]"]),
        RSU_A50_L_185_810_MSI_1="".join(results["[RSU_A50_L_185.810,1]"]),
        RSU_A50_L_185_810_MSI_2="".join(results["[RSU_A50_L_185.810,2]"]),
        RSU_A50_L_185_810_MSI_3="".join(results["[RSU_A50_L_185.810,3]"]),
        RSU_A50_L_186_410_MSI_1="".join(results["[RSU_A50_L_186.410,1]"]),
        RSU_A50_L_186_410_MSI_2="".join(results["[RSU_A50_L_186.410,2]"]),
        RSU_A50_L_186_410_MSI_3="".join(results["[RSU_A50_L_186.410,3]"]),
        RSU_A50_L_187_050_MSI_1="".join(results["[RSU_A50_L_187.050,1]"]),
        RSU_A50_L_187_050_MSI_2="".join(results["[RSU_A50_L_187.050,2]"]),
        RSU_A50_L_187_050_MSI_3="".join(results["[RSU_A50_L_187.050,3]"]),
        RSU_A50_L_187_750_MSI_1="".join(results["[RSU_A50_L_187.750,1]"]),
        RSU_A50_L_187_750_MSI_2="".join(results["[RSU_A50_L_187.750,2]"]),
        RSU_A50_L_187_750_MSI_3="".join(results["[RSU_A50_L_187.750,3]"]),
        RSU_A50_L_188_450_MSI_1="".join(results["[RSU_A50_L_188.450,1]"]),
        RSU_A50_L_188_450_MSI_2="".join(results["[RSU_A50_L_188.450,2]"]),
        RSU_A50_L_188_450_MSI_3="".join(results["[RSU_A50_L_188.450,3]"]),
        RSU_A50_L_189_150_MSI_1="".join(results["[RSU_A50_L_189.150,1]"]),
        RSU_A50_L_189_150_MSI_2="".join(results["[RSU_A50_L_189.150,2]"]),
        RSU_A50_L_189_150_MSI_3="".join(results["[RSU_A50_L_189.150,3]"]),
        RSU_A50_L_189_850_MSI_1="".join(results["[RSU_A50_L_189.850,1]"]),
        RSU_A50_L_189_850_MSI_2="".join(results["[RSU_A50_L_189.850,2]"]),
        RSU_A50_L_189_850_MSI_3="".join(results["[RSU_A50_L_189.850,3]"]),
        RSU_A50_L_190_550_MSI_1="".join(results["[RSU_A50_L_190.550,1]"]),
        RSU_A50_L_190_550_MSI_2="".join(results["[RSU_A50_L_190.550,2]"]),
        RSU_A50_L_190_550_MSI_3="".join(results["[RSU_A50_L_190.550,3]"]),
        RSU_A50_L_191_150_MSI_1="".join(results["[RSU_A50_L_191.150,1]"]),
        RSU_A50_L_191_150_MSI_2="".join(results["[RSU_A50_L_191.150,2]"]),
        RSU_A50_L_191_150_MSI_3="".join(results["[RSU_A50_L_191.150,3]"]),
        RSU_A50_L_191_750_MSI_1="".join(results["[RSU_A50_L_191.750,1]"]),
        RSU_A50_L_191_750_MSI_2="".join(results["[RSU_A50_L_191.750,2]"]),
        RSU_A50_L_191_750_MSI_3="".join(results["[RSU_A50_L_191.750,3]"]),
        RSU_A50_L_192_400_MSI_1="".join(results["[RSU_A50_L_192.400,1]"]),
        RSU_A50_L_192_400_MSI_2="".join(results["[RSU_A50_L_192.400,2]"]),
        RSU_A50_L_192_400_MSI_3="".join(results["[RSU_A50_L_192.400,3]"]),
        RSU_A50_L_193_000_MSI_1="".join(results["[RSU_A50_L_193.000,1]"]),
        RSU_A50_L_193_000_MSI_2="".join(results["[RSU_A50_L_193.000,2]"]),
        RSU_A50_L_193_000_MSI_3="".join(results["[RSU_A50_L_193.000,3]"]),
        RSU_A50_L_193_600_MSI_1="".join(results["[RSU_A50_L_193.600,1]"]),
        RSU_A50_L_193_600_MSI_2="".join(results["[RSU_A50_L_193.600,2]"]),
        RSU_A50_L_193_600_MSI_3="".join(results["[RSU_A50_L_193.600,3]"]),
        RSU_A50_L_194_153_MSI_1="".join(results["[RSU_A50_L_194.153,1]"]),
        RSU_A50_L_194_153_MSI_2="".join(results["[RSU_A50_L_194.153,2]"]),
        RSU_A50_L_194_153_MSI_3="".join(results["[RSU_A50_L_194.153,3]"]),
        RSU_A50_L_194_770_MSI_1="".join(results["[RSU_A50_L_194.770,1]"]),
        RSU_A50_L_194_770_MSI_2="".join(results["[RSU_A50_L_194.770,2]"]),
        RSU_A50_L_194_770_MSI_3="".join(results["[RSU_A50_L_194.770,3]"]),
        RSU_A50_L_195_270_MSI_1="".join(results["[RSU_A50_L_195.270,1]"]),
        RSU_A50_L_195_270_MSI_2="".join(results["[RSU_A50_L_195.270,2]"]),
        RSU_A50_L_195_270_MSI_3="".join(results["[RSU_A50_L_195.270,3]"]),
        RSU_A50_L_195_750_MSI_1="".join(results["[RSU_A50_L_195.750,1]"]),
        RSU_A50_L_195_750_MSI_2="".join(results["[RSU_A50_L_195.750,2]"]),
        RSU_A50_L_195_750_MSI_3="".join(results["[RSU_A50_L_195.750,3]"]),
        RSU_A50_L_196_350_MSI_1="".join(results["[RSU_A50_L_196.350,1]"]),
        RSU_A50_L_196_350_MSI_2="".join(results["[RSU_A50_L_196.350,2]"]),
        RSU_A50_L_196_350_MSI_3="".join(results["[RSU_A50_L_196.350,3]"]),
        RSU_A50_L_196_950_MSI_1="".join(results["[RSU_A50_L_196.950,1]"]),
        RSU_A50_L_196_950_MSI_2="".join(results["[RSU_A50_L_196.950,2]"]),
        RSU_A50_L_196_950_MSI_3="".join(results["[RSU_A50_L_196.950,3]"]),
        RSU_A50_L_197_578_MSI_1="".join(results["[RSU_A50_L_197.578,1]"]),
        RSU_A50_L_197_578_MSI_2="".join(results["[RSU_A50_L_197.578,2]"]),
        RSU_A50_L_197_578_MSI_3="".join(results["[RSU_A50_L_197.578,3]"]),
        RSU_A50_L_198_080_MSI_1="".join(results["[RSU_A50_L_198.080,1]"]),
        RSU_A50_L_198_080_MSI_2="".join(results["[RSU_A50_L_198.080,2]"]),
        RSU_A50_L_198_080_MSI_3="".join(results["[RSU_A50_L_198.080,3]"]),
        RSU_A50_L_198_545_MSI_1="".join(results["[RSU_A50_L_198.545,1]"]),
        RSU_A50_L_198_545_MSI_2="".join(results["[RSU_A50_L_198.545,2]"]),
        RSU_A50_L_198_545_MSI_3="".join(results["[RSU_A50_L_198.545,3]"]),
        RSU_A50_L_199_135_MSI_1="".join(results["[RSU_A50_L_199.135,1]"]),
        RSU_A50_L_199_135_MSI_2="".join(results["[RSU_A50_L_199.135,2]"]),
        RSU_A50_L_199_135_MSI_3="".join(results["[RSU_A50_L_199.135,3]"]),
        RSU_A50_L_199_810_MSI_1="".join(results["[RSU_A50_L_199.810,1]"]),
        RSU_A50_L_199_810_MSI_2="".join(results["[RSU_A50_L_199.810,2]"]),
        RSU_A50_L_199_810_MSI_3="".join(results["[RSU_A50_L_199.810,3]"]),
        RSU_A50_L_200_455_MSI_1="".join(results["[RSU_A50_L_200.455,1]"]),
        RSU_A50_L_200_455_MSI_2="".join(results["[RSU_A50_L_200.455,2]"]),
        RSU_A50_L_200_455_MSI_3="".join(results["[RSU_A50_L_200.455,3]"]),
        RSU_A50_L_201_050_MSI_1="".join(results["[RSU_A50_L_201.050,1]"]),
        RSU_A50_L_201_050_MSI_2="".join(results["[RSU_A50_L_201.050,2]"]),
        RSU_A50_L_201_050_MSI_3="".join(results["[RSU_A50_L_201.050,3]"]),
        RSU_A50_L_201_775_MSI_1="".join(results["[RSU_A50_L_201.775,1]"]),
        RSU_A50_L_201_775_MSI_2="".join(results["[RSU_A50_L_201.775,2]"]),
        RSU_A50_L_201_775_MSI_3="".join(results["[RSU_A50_L_201.775,3]"]),
        RSU_A50_L_202_375_MSI_1="".join(results["[RSU_A50_L_202.375,1]"]),
        RSU_A50_L_202_375_MSI_2="".join(results["[RSU_A50_L_202.375,2]"]),
        RSU_A50_L_202_375_MSI_3="".join(results["[RSU_A50_L_202.375,3]"]),
        RSU_A50_L_202_375_MSI_4="".join(results["[RSU_A50_L_202.375,4]"]),
        RSU_A50_w_182_890_MSI_1="".join(results["[RSU_A50_w_182.890,1]"]),
        RSU_A50_R_182_630_MSI_1="".join(results["[RSU_A50_R_182.630,1]"]),
        RSU_A50_R_182_630_MSI_2="".join(results["[RSU_A50_R_182.630,2]"]),
        RSU_A50_R_183_375_MSI_1="".join(results["[RSU_A50_R_183.375,1]"]),
        RSU_A50_R_183_375_MSI_2="".join(results["[RSU_A50_R_183.375,2]"]),
        RSU_A50_R_183_375_MSI_3="".join(results["[RSU_A50_R_183.375,3]"]),
        RSU_A50_R_183_800_MSI_1="".join(results["[RSU_A50_R_183.800,1]"]),
        RSU_A50_R_183_800_MSI_2="".join(results["[RSU_A50_R_183.800,2]"]),
        RSU_A50_R_183_800_MSI_3="".join(results["[RSU_A50_R_183.800,3]"]),
        RSU_A50_R_184_165_MSI_1="".join(results["[RSU_A50_R_184.165,1]"]),
        RSU_A50_R_184_165_MSI_2="".join(results["[RSU_A50_R_184.165,2]"]),
        RSU_A50_R_184_165_MSI_3="".join(results["[RSU_A50_R_184.165,3]"]),
        RSU_A50_R_184_715_MSI_1="".join(results["[RSU_A50_R_184.715,1]"]),
        RSU_A50_R_184_715_MSI_2="".join(results["[RSU_A50_R_184.715,2]"]),
        RSU_A50_R_184_715_MSI_3="".join(results["[RSU_A50_R_184.715,3]"]),
        RSU_A50_R_185_205_MSI_1="".join(results["[RSU_A50_R_185.205,1]"]),
        RSU_A50_R_185_205_MSI_2="".join(results["[RSU_A50_R_185.205,2]"]),
        RSU_A50_R_185_205_MSI_3="".join(results["[RSU_A50_R_185.205,3]"]),
        RSU_A50_R_185_810_MSI_1="".join(results["[RSU_A50_R_185.810,1]"]),
        RSU_A50_R_185_810_MSI_2="".join(results["[RSU_A50_R_185.810,2]"]),
        RSU_A50_R_185_810_MSI_3="".join(results["[RSU_A50_R_185.810,3]"]),
        RSU_A50_R_186_400_MSI_1="".join(results["[RSU_A50_R_186.400,1]"]),
        RSU_A50_R_186_400_MSI_2="".join(results["[RSU_A50_R_186.400,2]"]),
        RSU_A50_R_186_400_MSI_3="".join(results["[RSU_A50_R_186.400,3]"]),
        RSU_A50_R_187_050_MSI_1="".join(results["[RSU_A50_R_187.050,1]"]),
        RSU_A50_R_187_050_MSI_2="".join(results["[RSU_A50_R_187.050,2]"]),
        RSU_A50_R_187_050_MSI_3="".join(results["[RSU_A50_R_187.050,3]"]),
        RSU_A50_R_187_750_MSI_1="".join(results["[RSU_A50_R_187.750,1]"]),
        RSU_A50_R_187_750_MSI_2="".join(results["[RSU_A50_R_187.750,2]"]),
        RSU_A50_R_187_750_MSI_3="".join(results["[RSU_A50_R_187.750,3]"]),
        RSU_A50_R_188_450_MSI_1="".join(results["[RSU_A50_R_188.450,1]"]),
        RSU_A50_R_188_450_MSI_2="".join(results["[RSU_A50_R_188.450,2]"]),
        RSU_A50_R_188_450_MSI_3="".join(results["[RSU_A50_R_188.450,3]"]),
        RSU_A50_R_189_150_MSI_1="".join(results["[RSU_A50_R_189.150,1]"]),
        RSU_A50_R_189_150_MSI_2="".join(results["[RSU_A50_R_189.150,2]"]),
        RSU_A50_R_189_150_MSI_3="".join(results["[RSU_A50_R_189.150,3]"]),
        RSU_A50_R_189_850_MSI_1="".join(results["[RSU_A50_R_189.850,1]"]),
        RSU_A50_R_189_850_MSI_2="".join(results["[RSU_A50_R_189.850,2]"]),
        RSU_A50_R_189_850_MSI_3="".join(results["[RSU_A50_R_189.850,3]"]),
        RSU_A50_R_190_550_MSI_1="".join(results["[RSU_A50_R_190.550,1]"]),
        RSU_A50_R_190_550_MSI_2="".join(results["[RSU_A50_R_190.550,2]"]),
        RSU_A50_R_190_550_MSI_3="".join(results["[RSU_A50_R_190.550,3]"]),
        RSU_A50_R_191_150_MSI_1="".join(results["[RSU_A50_R_191.150,1]"]),
        RSU_A50_R_191_150_MSI_2="".join(results["[RSU_A50_R_191.150,2]"]),
        RSU_A50_R_191_150_MSI_3="".join(results["[RSU_A50_R_191.150,3]"]),
        RSU_A50_R_191_750_MSI_1="".join(results["[RSU_A50_R_191.750,1]"]),
        RSU_A50_R_191_750_MSI_2="".join(results["[RSU_A50_R_191.750,2]"]),
        RSU_A50_R_191_750_MSI_3="".join(results["[RSU_A50_R_191.750,3]"]),
        RSU_A50_R_192_400_MSI_1="".join(results["[RSU_A50_R_192.400,1]"]),
        RSU_A50_R_192_400_MSI_2="".join(results["[RSU_A50_R_192.400,2]"]),
        RSU_A50_R_192_400_MSI_3="".join(results["[RSU_A50_R_192.400,3]"]),
        RSU_A50_R_193_000_MSI_1="".join(results["[RSU_A50_R_193.000,1]"]),
        RSU_A50_R_193_000_MSI_2="".join(results["[RSU_A50_R_193.000,2]"]),
        RSU_A50_R_193_000_MSI_3="".join(results["[RSU_A50_R_193.000,3]"]),
        RSU_A50_R_193_600_MSI_1="".join(results["[RSU_A50_R_193.600,1]"]),
        RSU_A50_R_193_600_MSI_2="".join(results["[RSU_A50_R_193.600,2]"]),
        RSU_A50_R_193_600_MSI_3="".join(results["[RSU_A50_R_193.600,3]"]),
        RSU_A50_R_194_153_MSI_1="".join(results["[RSU_A50_R_194.153,1]"]),
        RSU_A50_R_194_153_MSI_2="".join(results["[RSU_A50_R_194.153,2]"]),
        RSU_A50_R_194_153_MSI_3="".join(results["[RSU_A50_R_194.153,3]"]),
        RSU_A50_R_194_630_MSI_1="".join(results["[RSU_A50_R_194.630,1]"]),
        RSU_A50_R_194_630_MSI_2="".join(results["[RSU_A50_R_194.630,2]"]),
        RSU_A50_R_194_630_MSI_3="".join(results["[RSU_A50_R_194.630,3]"]),
        RSU_A50_R_195_270_MSI_1="".join(results["[RSU_A50_R_195.270,1]"]),
        RSU_A50_R_195_270_MSI_2="".join(results["[RSU_A50_R_195.270,2]"]),
        RSU_A50_R_195_270_MSI_3="".join(results["[RSU_A50_R_195.270,3]"]),
        RSU_A50_R_195_750_MSI_1="".join(results["[RSU_A50_R_195.750,1]"]),
        RSU_A50_R_195_750_MSI_2="".join(results["[RSU_A50_R_195.750,2]"]),
        RSU_A50_R_195_750_MSI_3="".join(results["[RSU_A50_R_195.750,3]"]),
        RSU_A50_R_196_350_MSI_1="".join(results["[RSU_A50_R_196.350,1]"]),
        RSU_A50_R_196_350_MSI_2="".join(results["[RSU_A50_R_196.350,2]"]),
        RSU_A50_R_196_350_MSI_3="".join(results["[RSU_A50_R_196.350,3]"]),
        RSU_A50_R_197_062_MSI_1="".join(results["[RSU_A50_R_197.062,1]"]),
        RSU_A50_R_197_062_MSI_2="".join(results["[RSU_A50_R_197.062,2]"]),
        RSU_A50_R_197_062_MSI_3="".join(results["[RSU_A50_R_197.062,3]"]),
        RSU_A50_R_197_578_MSI_1="".join(results["[RSU_A50_R_197.578,1]"]),
        RSU_A50_R_197_578_MSI_2="".join(results["[RSU_A50_R_197.578,2]"]),
        RSU_A50_R_197_578_MSI_3="".join(results["[RSU_A50_R_197.578,3]"]),
        RSU_A50_R_198_080_MSI_1="".join(results["[RSU_A50_R_198.080,1]"]),
        RSU_A50_R_198_080_MSI_2="".join(results["[RSU_A50_R_198.080,2]"]),
        RSU_A50_R_198_080_MSI_3="".join(results["[RSU_A50_R_198.080,3]"]),
        RSU_A50_R_198_545_MSI_1="".join(results["[RSU_A50_R_198.545,1]"]),
        RSU_A50_R_198_545_MSI_2="".join(results["[RSU_A50_R_198.545,2]"]),
        RSU_A50_R_198_545_MSI_3="".join(results["[RSU_A50_R_198.545,3]"]),
        RSU_A50_R_199_135_MSI_1="".join(results["[RSU_A50_R_199.135,1]"]),
        RSU_A50_R_199_135_MSI_2="".join(results["[RSU_A50_R_199.135,2]"]),
        RSU_A50_R_199_135_MSI_3="".join(results["[RSU_A50_R_199.135,3]"]),
        RSU_A50_R_199_810_MSI_1="".join(results["[RSU_A50_R_199.810,1]"]),
        RSU_A50_R_199_810_MSI_2="".join(results["[RSU_A50_R_199.810,2]"]),
        RSU_A50_R_199_810_MSI_3="".join(results["[RSU_A50_R_199.810,3]"]),
        RSU_A50_R_200_455_MSI_1="".join(results["[RSU_A50_R_200.455,1]"]),
        RSU_A50_R_200_455_MSI_2="".join(results["[RSU_A50_R_200.455,2]"]),
        RSU_A50_R_200_455_MSI_3="".join(results["[RSU_A50_R_200.455,3]"]),
        RSU_A50_R_201_050_MSI_1="".join(results["[RSU_A50_R_201.050,1]"]),
        RSU_A50_R_201_050_MSI_2="".join(results["[RSU_A50_R_201.050,2]"]),
        RSU_A50_R_201_050_MSI_3="".join(results["[RSU_A50_R_201.050,3]"]),
        RSU_A50_R_201_775_MSI_1="".join(results["[RSU_A50_R_201.775,1]"]),
        RSU_A50_R_201_775_MSI_2="".join(results["[RSU_A50_R_201.775,2]"]),
        RSU_A50_R_201_775_MSI_3="".join(results["[RSU_A50_R_201.775,3]"]),
        RSU_A50_R_202_375_MSI_1="".join(results["[RSU_A50_R_202.375,1]"]),
        RSU_A50_R_202_375_MSI_2="".join(results["[RSU_A50_R_202.375,2]"]),
        RSU_A50_R_202_375_MSI_3="".join(results["[RSU_A50_R_202.375,3]"]),
        RSU_A50_R_202_375_MSI_4="".join(results["[RSU_A50_R_202.375,4]"])

    )

    empty_road = EMPTY_ROAD_TEMPLATE_A50.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Eight_Lane(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_EIGHT_LANE.format(
        RSU1_MSI1="".join(results["[RSU_A684_L_0_0,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_L_0_0,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_L_0_0,3]"]),
        RSU1_MSI4="".join(results["[RSU_A684_L_0_0,4]"]),
        RSU1_MSI5="".join(results["[RSU_A684_L_0_0,5]"]),
        RSU1_MSI6="".join(results["[RSU_A684_L_0_0,6]"]),
        RSU1_MSI7="".join(results["[RSU_A684_L_0_0,7]"]),
        RSU1_MSI8="".join(results["[RSU_A684_L_0_0,8]"]),

        RSU2_MSI1="".join(results["[RSU_A684_L_1_0,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_L_1_0,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_L_1_0,3]"]),
        RSU2_MSI4="".join(results["[RSU_A684_L_1_0,4]"]),
        RSU2_MSI5="".join(results["[RSU_A684_L_1_0,5]"]),
        RSU2_MSI6="".join(results["[RSU_A684_L_1_0,6]"]),
        RSU2_MSI7="".join(results["[RSU_A684_L_1_0,7]"]),
        RSU2_MSI8="".join(results["[RSU_A684_L_1_0,8]"]),

        RSU3_MSI1="".join(results["[RSU_A684_L_2_0,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_L_2_0,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_L_2_0,3]"]),
        RSU3_MSI4="".join(results["[RSU_A684_L_2_0,4]"]),
        RSU3_MSI5="".join(results["[RSU_A684_L_2_0,5]"]),
        RSU3_MSI6="".join(results["[RSU_A684_L_2_0,6]"]),
        RSU3_MSI7="".join(results["[RSU_A684_L_2_0,7]"]),
        RSU3_MSI8="".join(results["[RSU_A684_L_2_0,8]"]),

        RSU4_MSI1="".join(results["[RSU_A684_L_3_0,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_L_3_0,2]"]),
        RSU4_MSI3="".join(results["[RSU_A684_L_3_0,3]"]),
        RSU4_MSI4="".join(results["[RSU_A684_L_3_0,4]"]),
        RSU4_MSI5="".join(results["[RSU_A684_L_3_0,5]"]),
        RSU4_MSI6="".join(results["[RSU_A684_L_3_0,6]"]),
        RSU4_MSI7="".join(results["[RSU_A684_L_3_0,7]"]),
        RSU4_MSI8="".join(results["[RSU_A684_L_3_0,8]"]),

        RSU5_MSI1="".join(results["[RSU_A684_L_4_0,1]"]),
        RSU5_MSI2="".join(results["[RSU_A684_L_4_0,2]"]),
        RSU5_MSI3="".join(results["[RSU_A684_L_4_0,3]"]),
        RSU5_MSI4="".join(results["[RSU_A684_L_4_0,4]"]),
        RSU5_MSI5="".join(results["[RSU_A684_L_4_0,5]"]),
        RSU5_MSI6="".join(results["[RSU_A684_L_4_0,6]"]),
        RSU5_MSI7="".join(results["[RSU_A684_L_4_0,7]"]),
        RSU5_MSI8="".join(results["[RSU_A684_L_4_0,8]"]),

        RSU6_MSI1="".join(results["[RSU_A684_L_5_0,1]"]),
        RSU6_MSI2="".join(results["[RSU_A684_L_5_0,2]"]),
        RSU6_MSI3="".join(results["[RSU_A684_L_5_0,3]"]),
        RSU6_MSI4="".join(results["[RSU_A684_L_5_0,4]"]),
        RSU6_MSI5="".join(results["[RSU_A684_L_5_0,5]"]),
        RSU6_MSI6="".join(results["[RSU_A684_L_5_0,6]"]),
        RSU6_MSI7="".join(results["[RSU_A684_L_5_0,7]"]),
        RSU6_MSI8="".join(results["[RSU_A684_L_5_0,8]"]),

        RSU7_MSI1="".join(results["[RSU_A684_L_6_0,1]"]),
        RSU7_MSI2="".join(results["[RSU_A684_L_6_0,2]"]),
        RSU7_MSI3="".join(results["[RSU_A684_L_6_0,3]"]),
        RSU7_MSI4="".join(results["[RSU_A684_L_6_0,4]"]),
        RSU7_MSI5="".join(results["[RSU_A684_L_6_0,5]"]),
        RSU7_MSI6="".join(results["[RSU_A684_L_6_0,6]"]),
        RSU7_MSI7="".join(results["[RSU_A684_L_6_0,7]"]),
        RSU7_MSI8="".join(results["[RSU_A684_L_6_0,8]"]),

        RSU8_MSI1="".join(results["[RSU_A684_L_7_0,1]"]),
        RSU8_MSI2="".join(results["[RSU_A684_L_7_0,2]"]),
        RSU8_MSI3="".join(results["[RSU_A684_L_7_0,3]"]),
        RSU8_MSI4="".join(results["[RSU_A684_L_7_0,4]"]),
        RSU8_MSI5="".join(results["[RSU_A684_L_7_0,5]"]),
        RSU8_MSI6="".join(results["[RSU_A684_L_7_0,6]"]),
        RSU8_MSI7="".join(results["[RSU_A684_L_7_0,7]"]),
        RSU8_MSI8="".join(results["[RSU_A684_L_7_0,8]"]),

        RSU9_MSI1="".join(results["[RSU_A684_L_8_0,1]"]),
        RSU9_MSI2="".join(results["[RSU_A684_L_8_0,2]"]),
        RSU9_MSI3="".join(results["[RSU_A684_L_8_0,3]"]),
        RSU9_MSI4="".join(results["[RSU_A684_L_8_0,4]"]),
        RSU9_MSI5="".join(results["[RSU_A684_L_8_0,5]"]),
        RSU9_MSI6="".join(results["[RSU_A684_L_8_0,6]"]),
        RSU9_MSI7="".join(results["[RSU_A684_L_8_0,7]"]),
        RSU9_MSI8="".join(results["[RSU_A684_L_8_0,8]"]),

        RSU10_MSI1="".join(results["[RSU_A684_L_9_0,1]"]),
        RSU10_MSI2="".join(results["[RSU_A684_L_9_0,2]"]),
        RSU10_MSI3="".join(results["[RSU_A684_L_9_0,3]"]),
        RSU10_MSI4="".join(results["[RSU_A684_L_9_0,4]"]),
        RSU10_MSI5="".join(results["[RSU_A684_L_9_0,5]"]),
        RSU10_MSI6="".join(results["[RSU_A684_L_9_0,6]"]),
        RSU10_MSI7="".join(results["[RSU_A684_L_9_0,7]"]),
        RSU10_MSI8="".join(results["[RSU_A684_L_9_0,8]"]),

        RSU11_MSI1="".join(results["[RSU_A684_L_10_0,1]"]),
        RSU11_MSI2="".join(results["[RSU_A684_L_10_0,2]"]),
        RSU11_MSI3="".join(results["[RSU_A684_L_10_0,3]"]),
        RSU11_MSI4="".join(results["[RSU_A684_L_10_0,4]"]),
        RSU11_MSI5="".join(results["[RSU_A684_L_10_0,5]"]),
        RSU11_MSI6="".join(results["[RSU_A684_L_10_0,6]"]),
        RSU11_MSI7="".join(results["[RSU_A684_L_10_0,7]"]),
        RSU11_MSI8="".join(results["[RSU_A684_L_10_0,8]"]),

        RSU12_MSI1="".join(results["[RSU_A684_L_11_0,1]"]),
        RSU12_MSI2="".join(results["[RSU_A684_L_11_0,2]"]),
        RSU12_MSI3="".join(results["[RSU_A684_L_11_0,3]"]),
        RSU12_MSI4="".join(results["[RSU_A684_L_11_0,4]"]),
        RSU12_MSI5="".join(results["[RSU_A684_L_11_0,5]"]),
        RSU12_MSI6="".join(results["[RSU_A684_L_11_0,6]"]),
        RSU12_MSI7="".join(results["[RSU_A684_L_11_0,7]"]),
        RSU12_MSI8="".join(results["[RSU_A684_L_11_0,8]"]),

        RSU13_MSI1="".join(results["[RSU_A684_L_12_0,1]"]),
        RSU13_MSI2="".join(results["[RSU_A684_L_12_0,2]"]),
        RSU13_MSI3="".join(results["[RSU_A684_L_12_0,3]"]),
        RSU13_MSI4="".join(results["[RSU_A684_L_12_0,4]"]),
        RSU13_MSI5="".join(results["[RSU_A684_L_12_0,5]"]),
        RSU13_MSI6="".join(results["[RSU_A684_L_12_0,6]"]),
        RSU13_MSI7="".join(results["[RSU_A684_L_12_0,7]"]),
        RSU13_MSI8="".join(results["[RSU_A684_L_12_0,8]"]),

        RSU14_MSI1="".join(results["[RSU_A684_L_13_0,1]"]),
        RSU14_MSI2="".join(results["[RSU_A684_L_13_0,2]"]),
        RSU14_MSI3="".join(results["[RSU_A684_L_13_0,3]"]),
        RSU14_MSI4="".join(results["[RSU_A684_L_13_0,4]"]),
        RSU14_MSI5="".join(results["[RSU_A684_L_13_0,5]"]),
        RSU14_MSI6="".join(results["[RSU_A684_L_13_0,6]"]),
        RSU14_MSI7="".join(results["[RSU_A684_L_13_0,7]"]),
        RSU14_MSI8="".join(results["[RSU_A684_L_13_0,8]"]),

        RSU15_MSI1="".join(results["[RSU_A684_L_14_0,1]"]),
        RSU15_MSI2="".join(results["[RSU_A684_L_14_0,2]"]),
        RSU15_MSI3="".join(results["[RSU_A684_L_14_0,3]"]),
        RSU15_MSI4="".join(results["[RSU_A684_L_14_0,4]"]),
        RSU15_MSI5="".join(results["[RSU_A684_L_14_0,5]"]),
        RSU15_MSI6="".join(results["[RSU_A684_L_14_0,6]"]),
        RSU15_MSI7="".join(results["[RSU_A684_L_14_0,7]"]),
        RSU15_MSI8="".join(results["[RSU_A684_L_14_0,8]"]),

        RSU16_MSI1="".join(results["[RSU_A684_L_15_0,1]"]),
        RSU16_MSI2="".join(results["[RSU_A684_L_15_0,2]"]),
        RSU16_MSI3="".join(results["[RSU_A684_L_15_0,3]"]),
        RSU16_MSI4="".join(results["[RSU_A684_L_15_0,4]"]),
        RSU16_MSI5="".join(results["[RSU_A684_L_15_0,5]"]),
        RSU16_MSI6="".join(results["[RSU_A684_L_15_0,6]"]),
        RSU16_MSI7="".join(results["[RSU_A684_L_15_0,7]"]),
        RSU16_MSI8="".join(results["[RSU_A684_L_15_0,8]"]),

        RSU17_MSI1="".join(results["[RSU_A684_L_16_0,1]"]),
        RSU17_MSI2="".join(results["[RSU_A684_L_16_0,2]"]),
        RSU17_MSI3="".join(results["[RSU_A684_L_16_0,3]"]),
        RSU17_MSI4="".join(results["[RSU_A684_L_16_0,4]"]),
        RSU17_MSI5="".join(results["[RSU_A684_L_16_0,5]"]),
        RSU17_MSI6="".join(results["[RSU_A684_L_16_0,6]"]),
        RSU17_MSI7="".join(results["[RSU_A684_L_16_0,7]"]),
        RSU17_MSI8="".join(results["[RSU_A684_L_16_0,8]"]),

        RSU18_MSI1="".join(results["[RSU_A684_L_17_0,1]"]),
        RSU18_MSI2="".join(results["[RSU_A684_L_17_0,2]"]),
        RSU18_MSI3="".join(results["[RSU_A684_L_17_0,3]"]),
        RSU18_MSI4="".join(results["[RSU_A684_L_17_0,4]"]),
        RSU18_MSI5="".join(results["[RSU_A684_L_17_0,5]"]),
        RSU18_MSI6="".join(results["[RSU_A684_L_17_0,6]"]),
        RSU18_MSI7="".join(results["[RSU_A684_L_17_0,7]"]),
        RSU18_MSI8="".join(results["[RSU_A684_L_17_0,8]"]),

        RSU19_MSI1="".join(results["[RSU_A684_L_18_0,1]"]),
        RSU19_MSI2="".join(results["[RSU_A684_L_18_0,2]"]),
        RSU19_MSI3="".join(results["[RSU_A684_L_18_0,3]"]),
        RSU19_MSI4="".join(results["[RSU_A684_L_18_0,4]"]),
        RSU19_MSI5="".join(results["[RSU_A684_L_18_0,5]"]),
        RSU19_MSI6="".join(results["[RSU_A684_L_18_0,6]"]),
        RSU19_MSI7="".join(results["[RSU_A684_L_18_0,7]"]),
        RSU19_MSI8="".join(results["[RSU_A684_L_18_0,8]"]),

        RSU20_MSI1="".join(results["[RSU_A684_L_19_0,1]"]),
        RSU20_MSI2="".join(results["[RSU_A684_L_19_0,2]"]),
        RSU20_MSI3="".join(results["[RSU_A684_L_19_0,3]"]),
        RSU20_MSI4="".join(results["[RSU_A684_L_19_0,4]"]),
        RSU20_MSI5="".join(results["[RSU_A684_L_19_0,5]"]),
        RSU20_MSI6="".join(results["[RSU_A684_L_19_0,6]"]),
        RSU20_MSI7="".join(results["[RSU_A684_L_19_0,7]"]),
        RSU20_MSI8="".join(results["[RSU_A684_L_19_0,8]"]),

    )

    empty_road = EMPTY_ROAD_TEMPLATE_EIGHT_LANE.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Eight_Lane_2(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_EIGHT_LANE_2.format(
        RSU1_MSI1="".join(results["[RSU_A684_L_0_0,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_L_0_0,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_L_0_0,3]"]),
        RSU1_MSI4="".join(results["[RSU_A684_L_0_0,4]"]),
        RSU1_MSI5="".join(results["[RSU_A684_L_0_0,5]"]),
        RSU1_MSI6="".join(results["[RSU_A684_L_0_0,6]"]),
        RSU1_MSI7="".join(results["[RSU_A684_L_0_0,7]"]),
        RSU1_MSI8="".join(results["[RSU_A684_L_0_0,8]"]),

        RSU2_MSI1="".join(results["[RSU_A684_L_1_0,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_L_1_0,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_L_1_0,3]"]),
        RSU2_MSI4="".join(results["[RSU_A684_L_1_0,4]"]),
        RSU2_MSI5="".join(results["[RSU_A684_L_1_0,5]"]),
        RSU2_MSI6="".join(results["[RSU_A684_L_1_0,6]"]),
        RSU2_MSI7="".join(results["[RSU_A684_L_1_0,7]"]),
        RSU2_MSI8="".join(results["[RSU_A684_L_1_0,8]"]),

        RSU3_MSI1="".join(results["[RSU_A684_L_2_0,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_L_2_0,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_L_2_0,3]"]),
        RSU3_MSI4="".join(results["[RSU_A684_L_2_0,4]"]),
        RSU3_MSI5="".join(results["[RSU_A684_L_2_0,5]"]),
        RSU3_MSI6="".join(results["[RSU_A684_L_2_0,6]"]),
        RSU3_MSI7="".join(results["[RSU_A684_L_2_0,7]"]),
        RSU3_MSI8="".join(results["[RSU_A684_L_2_0,8]"]),

        RSU4_MSI1="".join(results["[RSU_A684_L_3_0,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_L_3_0,2]"]),
        RSU4_MSI3="".join(results["[RSU_A684_L_3_0,3]"]),
        RSU4_MSI4="".join(results["[RSU_A684_L_3_0,4]"]),
        RSU4_MSI5="".join(results["[RSU_A684_L_3_0,5]"]),
        RSU4_MSI6="".join(results["[RSU_A684_L_3_0,6]"]),
        RSU4_MSI7="".join(results["[RSU_A684_L_3_0,7]"]),
        RSU4_MSI8="".join(results["[RSU_A684_L_3_0,8]"]),

        RSU5_MSI1="".join(results["[RSU_A684_L_4_0,1]"]),
        RSU5_MSI2="".join(results["[RSU_A684_L_4_0,2]"]),
        RSU5_MSI3="".join(results["[RSU_A684_L_4_0,3]"]),
        RSU5_MSI4="".join(results["[RSU_A684_L_4_0,4]"]),
        RSU5_MSI5="".join(results["[RSU_A684_L_4_0,5]"]),
        RSU5_MSI6="".join(results["[RSU_A684_L_4_0,6]"]),
        RSU5_MSI7="".join(results["[RSU_A684_L_4_0,7]"]),
        RSU5_MSI8="".join(results["[RSU_A684_L_4_0,8]"]),

        RSU6_MSI1="".join(results["[RSU_A684_L_5_0,1]"]),
        RSU6_MSI2="".join(results["[RSU_A684_L_5_0,2]"]),
        RSU6_MSI3="".join(results["[RSU_A684_L_5_0,3]"]),
        RSU6_MSI4="".join(results["[RSU_A684_L_5_0,4]"]),
        RSU6_MSI5="".join(results["[RSU_A684_L_5_0,5]"]),
        RSU6_MSI6="".join(results["[RSU_A684_L_5_0,6]"]),
        RSU6_MSI7="".join(results["[RSU_A684_L_5_0,7]"]),
        RSU6_MSI8="".join(results["[RSU_A684_L_5_0,8]"]),

        RSU7_MSI1="".join(results["[RSU_A684_L_6_0,1]"]),
        RSU7_MSI2="".join(results["[RSU_A684_L_6_0,2]"]),
        RSU7_MSI3="".join(results["[RSU_A684_L_6_0,3]"]),
        RSU7_MSI4="".join(results["[RSU_A684_L_6_0,4]"]),
        RSU7_MSI5="".join(results["[RSU_A684_L_6_0,5]"]),
        RSU7_MSI6="".join(results["[RSU_A684_L_6_0,6]"]),
        RSU7_MSI7="".join(results["[RSU_A684_L_6_0,7]"]),
        RSU7_MSI8="".join(results["[RSU_A684_L_6_0,8]"]),

        RSU8_MSI1="".join(results["[RSU_A684_L_7_0,1]"]),
        RSU8_MSI2="".join(results["[RSU_A684_L_7_0,2]"]),
        RSU8_MSI3="".join(results["[RSU_A684_L_7_0,3]"]),
        RSU8_MSI4="".join(results["[RSU_A684_L_7_0,4]"]),
        RSU8_MSI5="".join(results["[RSU_A684_L_7_0,5]"]),
        RSU8_MSI6="".join(results["[RSU_A684_L_7_0,6]"]),
        RSU8_MSI7="".join(results["[RSU_A684_L_7_0,7]"]),
        RSU8_MSI8="".join(results["[RSU_A684_L_7_0,8]"]),

        RSU9_MSI1="".join(results["[RSU_A684_L_8_0,1]"]),
        RSU9_MSI2="".join(results["[RSU_A684_L_8_0,2]"]),
        RSU9_MSI3="".join(results["[RSU_A684_L_8_0,3]"]),
        RSU9_MSI4="".join(results["[RSU_A684_L_8_0,4]"]),
        RSU9_MSI5="".join(results["[RSU_A684_L_8_0,5]"]),
        RSU9_MSI6="".join(results["[RSU_A684_L_8_0,6]"]),
        RSU9_MSI7="".join(results["[RSU_A684_L_8_0,7]"]),
        RSU9_MSI8="".join(results["[RSU_A684_L_8_0,8]"]),

        RSU10_MSI1="".join(results["[RSU_A684_L_9_0,1]"]),
        RSU10_MSI2="".join(results["[RSU_A684_L_9_0,2]"]),
        RSU10_MSI3="".join(results["[RSU_A684_L_9_0,3]"]),
        RSU10_MSI4="".join(results["[RSU_A684_L_9_0,4]"]),
        RSU10_MSI5="".join(results["[RSU_A684_L_9_0,5]"]),
        RSU10_MSI6="".join(results["[RSU_A684_L_9_0,6]"]),
        RSU10_MSI7="".join(results["[RSU_A684_L_9_0,7]"]),
        RSU10_MSI8="".join(results["[RSU_A684_L_9_0,8]"]),

        RSU11_MSI1="".join(results["[RSU_A684_L_10_0,1]"]),
        RSU11_MSI2="".join(results["[RSU_A684_L_10_0,2]"]),
        RSU11_MSI3="".join(results["[RSU_A684_L_10_0,3]"]),
        RSU11_MSI4="".join(results["[RSU_A684_L_10_0,4]"]),
        RSU11_MSI5="".join(results["[RSU_A684_L_10_0,5]"]),
        RSU11_MSI6="".join(results["[RSU_A684_L_10_0,6]"]),
        RSU11_MSI7="".join(results["[RSU_A684_L_10_0,7]"]),
        RSU11_MSI8="".join(results["[RSU_A684_L_10_0,8]"]),

        RSU12_MSI1="".join(results["[RSU_A684_L_11_0,1]"]),
        RSU12_MSI2="".join(results["[RSU_A684_L_11_0,2]"]),
        RSU12_MSI3="".join(results["[RSU_A684_L_11_0,3]"]),
        RSU12_MSI4="".join(results["[RSU_A684_L_11_0,4]"]),
        RSU12_MSI5="".join(results["[RSU_A684_L_11_0,5]"]),
        RSU12_MSI6="".join(results["[RSU_A684_L_11_0,6]"]),
        RSU12_MSI7="".join(results["[RSU_A684_L_11_0,7]"]),
        RSU12_MSI8="".join(results["[RSU_A684_L_11_0,8]"]),

        RSU13_MSI1="".join(results["[RSU_A684_L_12_0,1]"]),
        RSU13_MSI2="".join(results["[RSU_A684_L_12_0,2]"]),
        RSU13_MSI3="".join(results["[RSU_A684_L_12_0,3]"]),
        RSU13_MSI4="".join(results["[RSU_A684_L_12_0,4]"]),
        RSU13_MSI5="".join(results["[RSU_A684_L_12_0,5]"]),
        RSU13_MSI6="".join(results["[RSU_A684_L_12_0,6]"]),
        RSU13_MSI7="".join(results["[RSU_A684_L_12_0,7]"]),
        RSU13_MSI8="".join(results["[RSU_A684_L_12_0,8]"]),

        RSU14_MSI1="".join(results["[RSU_A684_L_13_0,1]"]),
        RSU14_MSI2="".join(results["[RSU_A684_L_13_0,2]"]),
        RSU14_MSI3="".join(results["[RSU_A684_L_13_0,3]"]),
        RSU14_MSI4="".join(results["[RSU_A684_L_13_0,4]"]),
        RSU14_MSI5="".join(results["[RSU_A684_L_13_0,5]"]),
        RSU14_MSI6="".join(results["[RSU_A684_L_13_0,6]"]),
        RSU14_MSI7="".join(results["[RSU_A684_L_13_0,7]"]),
        RSU14_MSI8="".join(results["[RSU_A684_L_13_0,8]"]),

        RSU15_MSI1="".join(results["[RSU_A684_L_14_0,1]"]),
        RSU15_MSI2="".join(results["[RSU_A684_L_14_0,2]"]),
        RSU15_MSI3="".join(results["[RSU_A684_L_14_0,3]"]),
        RSU15_MSI4="".join(results["[RSU_A684_L_14_0,4]"]),
        RSU15_MSI5="".join(results["[RSU_A684_L_14_0,5]"]),
        RSU15_MSI6="".join(results["[RSU_A684_L_14_0,6]"]),
        RSU15_MSI7="".join(results["[RSU_A684_L_14_0,7]"]),
        RSU15_MSI8="".join(results["[RSU_A684_L_14_0,8]"]),

        RSU16_MSI1="".join(results["[RSU_A684_L_15_0,1]"]),
        RSU16_MSI2="".join(results["[RSU_A684_L_15_0,2]"]),
        RSU16_MSI3="".join(results["[RSU_A684_L_15_0,3]"]),
        RSU16_MSI4="".join(results["[RSU_A684_L_15_0,4]"]),
        RSU16_MSI5="".join(results["[RSU_A684_L_15_0,5]"]),
        RSU16_MSI6="".join(results["[RSU_A684_L_15_0,6]"]),
        RSU16_MSI7="".join(results["[RSU_A684_L_15_0,7]"]),
        RSU16_MSI8="".join(results["[RSU_A684_L_15_0,8]"]),

        RSU17_MSI1="".join(results["[RSU_A684_L_16_0,1]"]),
        RSU17_MSI2="".join(results["[RSU_A684_L_16_0,2]"]),
        RSU17_MSI3="".join(results["[RSU_A684_L_16_0,3]"]),
        RSU17_MSI4="".join(results["[RSU_A684_L_16_0,4]"]),
        RSU17_MSI5="".join(results["[RSU_A684_L_16_0,5]"]),
        RSU17_MSI6="".join(results["[RSU_A684_L_16_0,6]"]),
        RSU17_MSI7="".join(results["[RSU_A684_L_16_0,7]"]),
        RSU17_MSI8="".join(results["[RSU_A684_L_16_0,8]"]),

        RSU18_MSI1="".join(results["[RSU_A684_L_17_0,1]"]),
        RSU18_MSI2="".join(results["[RSU_A684_L_17_0,2]"]),
        RSU18_MSI3="".join(results["[RSU_A684_L_17_0,3]"]),
        RSU18_MSI4="".join(results["[RSU_A684_L_17_0,4]"]),
        RSU18_MSI5="".join(results["[RSU_A684_L_17_0,5]"]),
        RSU18_MSI6="".join(results["[RSU_A684_L_17_0,6]"]),
        RSU18_MSI7="".join(results["[RSU_A684_L_17_0,7]"]),
        RSU18_MSI8="".join(results["[RSU_A684_L_17_0,8]"]),

        RSU19_MSI1="".join(results["[RSU_A684_L_18_0,1]"]),
        RSU19_MSI2="".join(results["[RSU_A684_L_18_0,2]"]),
        RSU19_MSI3="".join(results["[RSU_A684_L_18_0,3]"]),
        RSU19_MSI4="".join(results["[RSU_A684_L_18_0,4]"]),
        RSU19_MSI5="".join(results["[RSU_A684_L_18_0,5]"]),
        RSU19_MSI6="".join(results["[RSU_A684_L_18_0,6]"]),
        RSU19_MSI7="".join(results["[RSU_A684_L_18_0,7]"]),
        RSU19_MSI8="".join(results["[RSU_A684_L_18_0,8]"]),

        RSU20_MSI1="".join(results["[RSU_A684_L_19_0,1]"]),
        RSU20_MSI2="".join(results["[RSU_A684_L_19_0,2]"]),
        RSU20_MSI3="".join(results["[RSU_A684_L_19_0,3]"]),
        RSU20_MSI4="".join(results["[RSU_A684_L_19_0,4]"]),
        RSU20_MSI5="".join(results["[RSU_A684_L_19_0,5]"]),
        RSU20_MSI6="".join(results["[RSU_A684_L_19_0,6]"]),
        RSU20_MSI7="".join(results["[RSU_A684_L_19_0,7]"]),
        RSU20_MSI8="".join(results["[RSU_A684_L_19_0,8]"]),

    )

    empty_road = EMPTY_ROAD_TEMPLATE_EIGHT_LANE_2.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_A15_Tunnel(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_A15_TUNNEL.format(
        RSU_A15_L_72_580_MSI_1="".join(results["[RSU_A15_L_72.580,1]"]),
        RSU_A15_L_72_580_MSI_2="".join(results["[RSU_A15_L_72.580,2]"]),
        RSU_A15_L_72_580_MSI_3="".join(results["[RSU_A15_L_72.580,3]"]),
        RSU_A15_L_72_580_MSI_4="".join(results["[RSU_A15_L_72.580,4]"]),
        RSU_A15_L_72_960_MSI_1="".join(results["[RSU_A15_L_72.960,1]"]),
        RSU_A15_L_72_960_MSI_2="".join(results["[RSU_A15_L_72.960,2]"]),
        RSU_A15_L_72_960_MSI_3="".join(results["[RSU_A15_L_72.960,3]"]),
        RSU_A15_L_72_960_MSI_4="".join(results["[RSU_A15_L_72.960,4]"]),
        RSU_A15_L_73_250_MSI_1="".join(results["[RSU_A15_L_73.250,1]"]),
        RSU_A15_L_73_250_MSI_2="".join(results["[RSU_A15_L_73.250,2]"]),
        RSU_A15_L_73_250_MSI_3="".join(results["[RSU_A15_L_73.250,3]"]),
        RSU_A15_L_73_250_MSI_4="".join(results["[RSU_A15_L_73.250,4]"]),
        RSU_A15_L_73_590_MSI_1="".join(results["[RSU_A15_L_73.590,1]"]),
        RSU_A15_L_73_590_MSI_2="".join(results["[RSU_A15_L_73.590,2]"]),
        RSU_A15_L_73_590_MSI_3="".join(results["[RSU_A15_L_73.590,3]"]),
        RSU_A15_L_73_755_MSI_1="".join(results["[RSU_A15_L_73.755,1]"]),
        RSU_A15_L_73_755_MSI_2="".join(results["[RSU_A15_L_73.755,2]"]),
        RSU_A15_L_73_755_MSI_3="".join(results["[RSU_A15_L_73.755,3]"]),
        RSU_A15_L_73_920_MSI_1="".join(results["[RSU_A15_L_73.920,1]"]),
        RSU_A15_L_73_920_MSI_2="".join(results["[RSU_A15_L_73.920,2]"]),
        RSU_A15_L_73_920_MSI_3="".join(results["[RSU_A15_L_73.920,3]"]),
        RSU_A15_L_74_085_MSI_1="".join(results["[RSU_A15_L_74.085,1]"]),
        RSU_A15_L_74_085_MSI_2="".join(results["[RSU_A15_L_74.085,2]"]),
        RSU_A15_L_74_085_MSI_3="".join(results["[RSU_A15_L_74.085,3]"]),
        RSU_A15_L_74_275_MSI_1="".join(results["[RSU_A15_L_74.275,1]"]),
        RSU_A15_L_74_275_MSI_2="".join(results["[RSU_A15_L_74.275,2]"]),
        RSU_A15_L_74_275_MSI_3="".join(results["[RSU_A15_L_74.275,3]"]),
        RSU_A15_L_74_625_MSI_1="".join(results["[RSU_A15_L_74.625,1]"]),
        RSU_A15_L_74_625_MSI_2="".join(results["[RSU_A15_L_74.625,2]"]),
        RSU_A15_L_74_625_MSI_3="".join(results["[RSU_A15_L_74.625,3]"]),
        RSU_A15_L_75_075_MSI_1="".join(results["[RSU_A15_L_75.075,1]"]),
        RSU_A15_L_75_075_MSI_2="".join(results["[RSU_A15_L_75.075,2]"]),
        RSU_A15_L_75_075_MSI_3="".join(results["[RSU_A15_L_75.075,3]"]),
        RSU_A15_L_75_375_MSI_1="".join(results["[RSU_A15_L_75.375,1]"]),
        RSU_A15_L_75_375_MSI_2="".join(results["[RSU_A15_L_75.375,2]"]),
        RSU_A15_L_75_375_MSI_3="".join(results["[RSU_A15_L_75.375,3]"]),
        RSU_A15_L_75_375_MSI_4="".join(results["[RSU_A15_L_75.375,4]"]),
        RSU_A15_L_75_860_MSI_1="".join(results["[RSU_A15_L_75.860,1]"]),
        RSU_A15_L_75_860_MSI_2="".join(results["[RSU_A15_L_75.860,2]"]),
        RSU_A15_L_75_860_MSI_3="".join(results["[RSU_A15_L_75.860,3]"]),
        RSU_A15_L_76_310_MSI_1="".join(results["[RSU_A15_L_76.310,1]"]),
        RSU_A15_L_76_310_MSI_2="".join(results["[RSU_A15_L_76.310,2]"]),
        RSU_A15_L_76_310_MSI_3="".join(results["[RSU_A15_L_76.310,3]"]),
        RSU_A15_L_76_745_MSI_1="".join(results["[RSU_A15_L_76.745,1]"]),
        RSU_A15_L_76_745_MSI_2="".join(results["[RSU_A15_L_76.745,2]"]),
        RSU_A15_L_76_745_MSI_3="".join(results["[RSU_A15_L_76.745,3]"]),
        RSU_A15_L_76_745_MSI_4="".join(results["[RSU_A15_L_76.745,4]"]),
        RSU_A15_L_77_045_MSI_1="".join(results["[RSU_A15_L_77.045,1]"]),
        RSU_A15_L_77_045_MSI_2="".join(results["[RSU_A15_L_77.045,2]"]),
        RSU_A15_L_77_045_MSI_3="".join(results["[RSU_A15_L_77.045,3]"]),
        RSU_A15_L_77_045_MSI_4="".join(results["[RSU_A15_L_77.045,4]"]),
        RSU_A15_L_77_480_MSI_1="".join(results["[RSU_A15_L_77.480,1]"]),
        RSU_A15_L_77_480_MSI_2="".join(results["[RSU_A15_L_77.480,2]"]),
        RSU_A15_L_77_480_MSI_3="".join(results["[RSU_A15_L_77.480,3]"]),
        RSU_A15_L_77_780_MSI_1="".join(results["[RSU_A15_L_77.780,1]"]),
        RSU_A15_L_77_780_MSI_2="".join(results["[RSU_A15_L_77.780,2]"]),
        RSU_A15_L_77_780_MSI_3="".join(results["[RSU_A15_L_77.780,3]"]),
        RSU_A15_R_72_540_MSI_1="".join(results["[RSU_A15_R_72.540,1]"]),
        RSU_A15_R_72_540_MSI_2="".join(results["[RSU_A15_R_72.540,2]"]),
        RSU_A15_R_72_540_MSI_3="".join(results["[RSU_A15_R_72.540,3]"]),
        RSU_A15_R_72_960_MSI_1="".join(results["[RSU_A15_R_72.960,1]"]),
        RSU_A15_R_72_960_MSI_2="".join(results["[RSU_A15_R_72.960,2]"]),
        RSU_A15_R_72_960_MSI_3="".join(results["[RSU_A15_R_72.960,3]"]),
        RSU_A15_R_73_250_MSI_1="".join(results["[RSU_A15_R_73.250,1]"]),
        RSU_A15_R_73_250_MSI_2="".join(results["[RSU_A15_R_73.250,2]"]),
        RSU_A15_R_73_250_MSI_3="".join(results["[RSU_A15_R_73.250,3]"]),
        RSU_A15_R_73_590_MSI_1="".join(results["[RSU_A15_R_73.590,1]"]),
        RSU_A15_R_73_590_MSI_2="".join(results["[RSU_A15_R_73.590,2]"]),
        RSU_A15_R_73_590_MSI_3="".join(results["[RSU_A15_R_73.590,3]"]),
        RSU_A15_R_73_755_MSI_1="".join(results["[RSU_A15_R_73.755,1]"]),
        RSU_A15_R_73_755_MSI_2="".join(results["[RSU_A15_R_73.755,2]"]),
        RSU_A15_R_73_755_MSI_3="".join(results["[RSU_A15_R_73.755,3]"]),
        RSU_A15_R_73_920_MSI_1="".join(results["[RSU_A15_R_73.920,1]"]),
        RSU_A15_R_73_920_MSI_2="".join(results["[RSU_A15_R_73.920,2]"]),
        RSU_A15_R_73_920_MSI_3="".join(results["[RSU_A15_R_73.920,3]"]),
        RSU_A15_R_74_085_MSI_1="".join(results["[RSU_A15_R_74.085,1]"]),
        RSU_A15_R_74_085_MSI_2="".join(results["[RSU_A15_R_74.085,2]"]),
        RSU_A15_R_74_085_MSI_3="".join(results["[RSU_A15_R_74.085,3]"]),
        RSU_A15_R_74_245_MSI_1="".join(results["[RSU_A15_R_74.245,1]"]),
        RSU_A15_R_74_245_MSI_2="".join(results["[RSU_A15_R_74.245,2]"]),
        RSU_A15_R_74_245_MSI_3="".join(results["[RSU_A15_R_74.245,3]"]),
        RSU_A15_R_74_245_MSI_4="".join(results["[RSU_A15_R_74.245,4]"]),
        RSU_A15_R_74_625_MSI_1="".join(results["[RSU_A15_R_74.625,1]"]),
        RSU_A15_R_74_625_MSI_2="".join(results["[RSU_A15_R_74.625,2]"]),
        RSU_A15_R_74_625_MSI_3="".join(results["[RSU_A15_R_74.625,3]"]),
        RSU_A15_R_74_625_MSI_4="".join(results["[RSU_A15_R_74.625,4]"]),
        RSU_A15_R_75_075_MSI_1="".join(results["[RSU_A15_R_75.075,1]"]),
        RSU_A15_R_75_075_MSI_2="".join(results["[RSU_A15_R_75.075,2]"]),
        RSU_A15_R_75_075_MSI_3="".join(results["[RSU_A15_R_75.075,3]"]),
        RSU_A15_R_75_075_MSI_4="".join(results["[RSU_A15_R_75.075,4]"]),
        RSU_A15_R_75_375_MSI_1="".join(results["[RSU_A15_R_75.375,1]"]),
        RSU_A15_R_75_375_MSI_2="".join(results["[RSU_A15_R_75.375,2]"]),
        RSU_A15_R_75_375_MSI_3="".join(results["[RSU_A15_R_75.375,3]"]),
        RSU_A15_R_75_375_MSI_4="".join(results["[RSU_A15_R_75.375,4]"]),
        RSU_A15_R_75_675_MSI_1="".join(results["[RSU_A15_R_75.675,1]"]),
        RSU_A15_R_75_675_MSI_2="".join(results["[RSU_A15_R_75.675,2]"]),
        RSU_A15_R_75_675_MSI_3="".join(results["[RSU_A15_R_75.675,3]"]),
        RSU_A15_R_76_410_MSI_1="".join(results["[RSU_A15_R_76.410,1]"]),
        RSU_A15_R_76_410_MSI_2="".join(results["[RSU_A15_R_76.410,2]"]),
        RSU_A15_R_76_410_MSI_3="".join(results["[RSU_A15_R_76.410,3]"]),
        RSU_A15_R_77_003_MSI_1="".join(results["[RSU_A15_R_77.003,1]"]),
        RSU_A15_R_77_003_MSI_2="".join(results["[RSU_A15_R_77.003,2]"]),
        RSU_A15_R_77_003_MSI_3="".join(results["[RSU_A15_R_77.003,3]"]),
        RSU_A15_R_77_700_MSI_1="".join(results["[RSU_A15_R_77.700,1]"]),
        RSU_A15_R_77_700_MSI_2="".join(results["[RSU_A15_R_77.700,2]"]),
        RSU_A15_R_77_700_MSI_3="".join(results["[RSU_A15_R_77.700,3]"]),
        RSU_A15_R_77_700_MSI_4="".join(results["[RSU_A15_R_77.700,4]"])
    )

    empty_road = EMPTY_ROAD_TEMPLATE_A15_TUNNEL.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Circle(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_CIRCLE.format(
        RSU0_MSI1="".join(results["[RSU_A684_L_0_0,1]"]),
        RSU0_MSI2="".join(results["[RSU_A684_L_0_0,2]"]),
        RSU0_MSI3="".join(results["[RSU_A684_L_0_0,3]"]),

        RSU1_MSI1="".join(results["[RSU_A684_L_1_0,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_L_1_0,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_L_1_0,3]"]),

        RSU2_MSI1="".join(results["[RSU_A684_L_2_0,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_L_2_0,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_L_2_0,3]"]),

        RSU3_MSI1="".join(results["[RSU_A684_L_3_0,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_L_3_0,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_L_3_0,3]"]),

        RSU4_MSI1="".join(results["[RSU_A684_L_4_0,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_L_4_0,2]"]),
        RSU4_MSI3="".join(results["[RSU_A684_L_4_0,3]"]),

        RSU5_MSI1="".join(results["[RSU_A684_L_5_0,1]"]),
        RSU5_MSI2="".join(results["[RSU_A684_L_5_0,2]"]),
        RSU5_MSI3="".join(results["[RSU_A684_L_5_0,3]"]),

    )

    empty_road = EMPTY_ROAD_TEMPLATE_CIRCLE.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Demo(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_FOUR_LANE.format(
        RSU1_MSI1="".join(results["[RSU_A684_L_0_0,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_L_0_0,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_L_0_0,3]"]),
        RSU1_MSI4="".join(results["[RSU_A684_L_0_0,4]"]),

        RSU2_MSI1="".join(results["[RSU_A684_L_1_0,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_L_1_0,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_L_1_0,3]"]),
        RSU2_MSI4="".join(results["[RSU_A684_L_1_0,4]"]),

        RSU3_MSI1="".join(results["[RSU_A684_L_2_0,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_L_2_0,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_L_2_0,3]"]),
        RSU3_MSI4="".join(results["[RSU_A684_L_2_0,4]"]),

        RSU4_MSI1="".join(results["[RSU_A684_L_3_0,1]"]),
        RSU4_MSI2="".join(results["[RSU_A684_L_3_0,2]"]),
        RSU4_MSI3="".join(results["[RSU_A684_L_3_0,3]"]),
        RSU4_MSI4="".join(results["[RSU_A684_L_3_0,4]"]),

        RSU5_MSI1="".join(results["[RSU_A684_L_4_0,1]"]),
        RSU5_MSI2="".join(results["[RSU_A684_L_4_0,2]"]),
        RSU5_MSI3="".join(results["[RSU_A684_L_4_0,3]"]),
        RSU5_MSI4="".join(results["[RSU_A684_L_4_0,4]"]),

        RSU6_MSI1="".join(results["[RSU_A684_L_5_0,1]"]),
        RSU6_MSI2="".join(results["[RSU_A684_L_5_0,2]"]),
        RSU6_MSI3="".join(results["[RSU_A684_L_5_0,3]"]),
        RSU6_MSI4="".join(results["[RSU_A684_L_5_0,4]"]),

        RSU7_MSI1="".join(results["[RSU_A684_L_6_0,1]"]),
        RSU7_MSI2="".join(results["[RSU_A684_L_6_0,2]"]),
        RSU7_MSI3="".join(results["[RSU_A684_L_6_0,3]"]),
        RSU7_MSI4="".join(results["[RSU_A684_L_6_0,4]"])
    )

    empty_road = EMPTY_ROAD_TEMPLATE_FOUR_LANE.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data


def createSVG_Demo2(model, json_data):
    results, json_data = getMyVars(model, json_data)

    code = ROAD_TEMPLATE_FOUR_FIVE_LANE.format(
        RSU1_MSI1="".join(results["[RSU_A684_L_0_0,1]"]),
        RSU1_MSI2="".join(results["[RSU_A684_L_0_0,2]"]),
        RSU1_MSI3="".join(results["[RSU_A684_L_0_0,3]"]),
        RSU1_MSI4="".join(results["[RSU_A684_L_0_0,4]"]),

        RSU2_MSI1="".join(results["[RSU_A684_L_1_0,1]"]),
        RSU2_MSI2="".join(results["[RSU_A684_L_1_0,2]"]),
        RSU2_MSI3="".join(results["[RSU_A684_L_1_0,3]"]),
        RSU2_MSI4="".join(results["[RSU_A684_L_1_0,4]"]),

        RSU3_MSI1="".join(results["[RSU_A684_L_2_0,1]"]),
        RSU3_MSI2="".join(results["[RSU_A684_L_2_0,2]"]),
        RSU3_MSI3="".join(results["[RSU_A684_L_2_0,3]"]),
        RSU3_MSI4="".join(results["[RSU_A684_L_2_0,4]"]),

        RSU4_MSI0="".join(results["[RSU_A684_L_3_0,1]"]),
        RSU4_MSI1="".join(results["[RSU_A684_L_3_0,2]"]),
        RSU4_MSI2="".join(results["[RSU_A684_L_3_0,3]"]),
        RSU4_MSI3="".join(results["[RSU_A684_L_3_0,4]"]),
        RSU4_MSI4="".join(results["[RSU_A684_L_3_0,5]"]),

        RSU5_MSI0="".join(results["[RSU_A684_L_4_0,1]"]),
        RSU5_MSI1="".join(results["[RSU_A684_L_4_0,2]"]),
        RSU5_MSI2="".join(results["[RSU_A684_L_4_0,3]"]),
        RSU5_MSI3="".join(results["[RSU_A684_L_4_0,4]"]),
        RSU5_MSI4="".join(results["[RSU_A684_L_4_0,5]"]),

        RSU6_MSI0="".join(results["[RSU_A684_L_5_0,1]"]),
        RSU6_MSI1="".join(results["[RSU_A684_L_5_0,2]"]),
        RSU6_MSI2="".join(results["[RSU_A684_L_5_0,3]"]),
        RSU6_MSI3="".join(results["[RSU_A684_L_5_0,4]"]),
        RSU6_MSI4="".join(results["[RSU_A684_L_5_0,5]"]),

        RSU7_MSI0="".join(results["[RSU_A684_L_6_0,1]"]),
        RSU7_MSI1="".join(results["[RSU_A684_L_6_0,2]"]),
        RSU7_MSI2="".join(results["[RSU_A684_L_6_0,3]"]),
        RSU7_MSI3="".join(results["[RSU_A684_L_6_0,4]"]),
        RSU7_MSI4="".join(results["[RSU_A684_L_6_0,5]"])
    )

    empty_road = EMPTY_ROAD_TEMPLATE_FOUR_FIVE_LANE.format(
        content="".join(code)
    )

    svg = DEFS_TEMPLATE.format(
        content="".join(empty_road)
    )

    return svg, json_data
