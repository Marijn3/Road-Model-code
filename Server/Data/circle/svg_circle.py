EMPTY_ROAD_TEMPLATE_CIRCLE = '''<g id="Road Surface">
      <rect
       style="fill:#7b797b;fill-opacity:1;stroke:none;"
       width="70"
       height="200"
       x="10"
       y="5" />

       <rect
       style="fill:#395052;fill-opacity:1;stroke:none"
       width="15"
       height="200"
       x="80"
       y="5" />
      
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 10,5 V 205"
         id="path1909" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 30,5 V 205"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 50,5 V 205"
         id="path1909-7" />
         <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 70,5 V 205"
         id="path1909-8" />
   </g> 

   <g id="nametags_MSI"
      style="font-size:8px;line-height:1.25;font-family:sans-serif">
   </g>


   <g id="legends_MSIs">
      {content}
   </g>'''

ROAD_TEMPLATE_CIRCLE = '''
<g id='RSU20'
  transform="translate(0,10)">
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
</g>
<g id='RSU19'
  transform="translate(0,40)">
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
</g>      
<g id='RSU18'
  transform="translate(0,70)">
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
</g>
<g id='RSU17'
  transform="translate(0,100)">
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
</g>      
<g id='RSU16'
  transform="translate(0,130)">
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
</g>
<g id='RSU15'
  transform="translate(0,160)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU0_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU0_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU0_MSI3}
  </g>
</g>            
      ''' 