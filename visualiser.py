from functions import *
import svgwrite

LANE_WIDTH = 5
offset_x = 148000
offset_y = 407000
scale_factor = 0.2


def move_coord(c: tuple) -> tuple:
    return (c[0] - offset_x) * scale_factor, (c[1] - offset_y) * scale_factor


def shapely_to_svg(geom, prop, svg_elem):
    if isinstance(prop['nLanes'], int):
        road_width = LANE_WIDTH*prop['nLanes']
        # print([type(coord) for coord in geom.coords])
        line_coordinates = [move_coord(coordinate) for coordinate in geom.coords]
        roadline = svgwrite.shapes.Polyline(points=line_coordinates, stroke='grey', fill="none", stroke_width=road_width)
        svg_elem.add(roadline)
    else:
        road_width = LANE_WIDTH * 2
        line_coordinates = [move_coord(coordinate) for coordinate in geom.coords]
        roadline = svgwrite.shapes.Polyline(points=line_coordinates, stroke='red', fill="none",
                                            stroke_width=road_width)
        svg_elem.add(roadline)


# Load all files and store the GeoDataFrames in the class
dfl = DataFrameLoader()
dfl.load_data_frames("Vught")

road = RoadModel()
road.import_dataframes(dfl)

# Create SVG drawing
svg_drawing = svgwrite.Drawing(filename="geometries.svg")

sections = road.get_sections()
for section in sections:
    shapely_to_svg(section['geometry'], section['properties'], svg_drawing)

#print(dfl.extent)

# Save SVG file
svg_drawing.save()
