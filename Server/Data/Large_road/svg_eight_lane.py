EMPTY_ROAD_TEMPLATE_EIGHT_LANE = '''<g id="Road Surface">
      <rect
       style="fill:#7b797b;fill-opacity:1;stroke:none;"
       width="160"
       height="615"
       x="10"
       y="5" />

       <rect
       style="fill:#395052;fill-opacity:1;stroke:none"
       width="15"
       height="615"
       x="170"
       y="5" />
      
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 10,5 V 620"
         id="path1909" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 30,5 V 620"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 50,5 V 620"
         id="path1909-7" />
         <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 70,5 V 620"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 90,5 V 620"
         id="path1909-7" />
         <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 110,5 V 620"
         id="path1909-8" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 130,5 V 620"
         id="path1909-7" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:12,12"
         d="M 150,5 V 620"
         id="path1909-7" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 170,5  V 620"
         id="path1909-6" />
      <path
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="M 185,5  V 620"
         id="path1909-6" />
   </g> 

   <g id="nametags_MSI"
      style="font-size:8px;line-height:1.25;font-family:sans-serif">
   </g>


   <g id="legends_MSIs">
      {content}
   </g>'''

ROAD_TEMPLATE_EIGHT_LANE = '''
<g id='RSU20'
  transform="translate(0,10)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU20_MSI8}
  </g>
</g>
<g id='RSU19'
  transform="translate(0,40)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU19_MSI8}
  </g>
</g>      
<g id='RSU18'
  transform="translate(0,70)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU18_MSI8}
  </g>
</g>
<g id='RSU17'
  transform="translate(0,100)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU17_MSI8}
  </g>
</g>      
<g id='RSU16'
  transform="translate(0,130)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU16_MSI8}
  </g>
</g>
<g id='RSU15'
  transform="translate(0,160)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU15_MSI8}
  </g>
</g>
<g id='RSU14'
  transform="translate(0,190)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU14_MSI8}
  </g>
</g>
<g id='RSU13'
  transform="translate(0,220)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU13_MSI8}
  </g>
</g>
<g id='RSU12'
  transform="translate(0,250)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU12_MSI8}
  </g>
</g>
<g id='RSU11'
  transform="translate(0,280)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU11_MSI8}
  </g>
</g>      
<g id='RSU10'
  transform="translate(0,310)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU10_MSI8}
  </g>
</g>
<g id='RSU9'
  transform="translate(0,340)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU9_MSI8}
  </g>
</g>      
<g id='RSU8'
  transform="translate(0,370)">
  <g transform="translate(12.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI1}
  </g>
  <g transform="translate(32.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI2}
  </g>
  <g transform="translate(52.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI3}
  </g>
  <g transform="translate(72.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI4}
  </g>
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU8_MSI8}
  </g>
</g>
<g id='RSU7'
  transform="translate(0,400)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU7_MSI8}
  </g>
</g>      
<g id='RSU6'
  transform="translate(0,430)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU6_MSI8}
  </g>
</g>
<g id='RSU5'
  transform="translate(0,460)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU5_MSI8}
  </g>
</g>
<g id='RSU4'
  transform="translate(0,490)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU4_MSI8}
  </g>
</g>
<g id='RSU3'
  transform="translate(0,520)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU3_MSI8}
  </g>
</g>
<g id='RSU2'
  transform="translate(0,550)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU2_MSI8}
  </g>
</g>
<g id='RSU1'
  transform="translate(0,580)">
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
  <g transform="translate(92.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI5}
  </g>
  <g transform="translate(112.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI6}
  </g>
  <g transform="translate(132.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI7}
  </g>
  <g transform="translate(152.5,0)">
    <use href="#template_legend_blank" />
    {RSU1_MSI8}
  </g>
</g>            
      ''' 
