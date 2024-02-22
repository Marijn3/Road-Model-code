EMPTY_ROAD_TEMPLATE_FOUR_FIVE_LANE = '''<g id="Road Surface">
      <rect
       style="fill:#7b797b;fill-opacity:1;stroke:none;"
       width="80"
       height="215"
       x="10"
       y="5" />

       <rect
       style="fill:#395052;fill-opacity:1;stroke:none"
       width="15"
       height="215"
       x="90"
       y="5" />
      
      <path
         style="fill:#7b797b;fill-opacity:1;stroke:none"
         d="M -10,115 v-110 h 40 v 140 Z"
         id="path1909a" />
      
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M -10,5 V 115 l 20,15 V 220"
         id="path1909b" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 10,5 V 130"
         id="path1909c" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 30,5 V 220"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 50,5 V 220"
         id="path1909-7" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 70,5 V 220"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 90,5  V 220"
         id="path1909-6" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 105,5  V 220"
         id="path1909-6" />
   </g> 

   <g id="nametags_MSI"
      style="font-size:8px;line-height:1.25;font-family:sans-serif">
   </g>


   <g id="legends_MSIs">
      {content}
   </g>'''

ROAD_TEMPLATE_FOUR_FIVE_LANE = '''
<g id='RSU7'
  transform="translate(0,10)">
  <g transform="translate(-7.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI0}
  </g>
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI4}
  </g>
</g>      
<g id='RSU6'
  transform="translate(0,40)">
  <g transform="translate(-7.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI0}
  </g>
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI4}
  </g>
</g>
<g id='RSU5'
  transform="translate(0,70)">
  <g transform="translate(-7.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI0}
  </g>
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI4}
  </g>
</g>
<g id='RSU4'
  transform="translate(0,100)">
  <g transform="translate(-7.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI0}
  </g>
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI4}
  </g>
</g>
<g id='RSU3'
  transform="translate(0,130)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI4}
  </g>
</g>
<g id='RSU2'
  transform="translate(0,160)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI4}
  </g>
</g>
<g id='RSU1'
  transform="translate(0,190)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI4}
  </g>
</g>
      ''' 
