EMPTY_ROAD_TEMPLATE_TEST_RHL = '''<g id="Road Surface">
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 10,5 V 120"
         id="path1909" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 30,5 V 120"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:22,2"
         d="M 50,15 V 120"
         id="path1909-7" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 50,5 V 10 L 70,35 V 120"
         id="path1909-6" />
   </g> 

   <g id="nametags_MSI"
      style="font-size:8px;line-height:1.25;font-family:sans-serif">
   </g>


   <g id="legends_MSIs">
      {content}
   </g>'''

ROAD_TEMPLATE_TEST_RHL = '''
      <g id='RSU_4'>
         <g id="MSI_1"
            transform="translate(12.5,10)">
            <use href="#template_legend_blank" />
            {RSU4_MSI1}
         </g>
         <g id="MSI_2"
            transform="translate(32.5,10)">
            <use href="#template_legend_blank" />
            {RSU4_MSI2}
         </g>
      </g>
      <g id='RSU_3'>
         <g id="MSI_1"
            transform="translate(12.5,40)">
            <use href="#template_legend_blank" />
            {RSU3_MSI1}
         </g>
         <g id="MSI_2"
            transform="translate(32.5,40)">
            <use href="#template_legend_blank" />
            {RSU3_MSI2}
         </g>
         
         <g id="MSI_3"
            transform="translate(52.5,40)">
            <use href="#template_legend_blank" />
            {RSU3_MSI3}
         </g>
      </g>
      <g id='RSU_2'>
         <g id="MSI_1"
            transform="translate(12.5,70)">
            <use href="#template_legend_blank" />
            {RSU2_MSI1}
         </g>
         <g id="MSI_2"
            transform="translate(32.5,70)">
            <use href="#template_legend_blank" />
            {RSU2_MSI2}
         </g>
         
         <g id="MSI_3"
            transform="translate(52.5,70)">
            <use href="#template_legend_blank" />
            {RSU2_MSI3}
         </g>
      </g>
      <g id='RSU_1'>
         <g id="MSI_1"
            transform="translate(12.5,100)">
            <use href="#template_legend_blank" />
            {RSU1_MSI1}
         </g>
         <g id="MSI_2"
            transform="translate(32.5,100)">
            <use href="#template_legend_blank" />
            {RSU1_MSI2}
         </g>
         
         <g id="MSI_3"
            transform="translate(52.5,100)">
            <use href="#template_legend_blank" />
            {RSU1_MSI3}
         </g>
      </g>''' 
