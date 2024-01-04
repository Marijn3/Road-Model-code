from shapely import *


def ConvertToLineString(mls: MultiLineString) -> LineString:
    """
    Converts MultiLineString objects resulting fron the intersection function into LineStrings.
    Args:
        mls (shapely.MultiLineString): The MultiLineString geometry.
    Returns:
        LineString: LineString representation of the same MultiLineString.
    Note:
        The function expects a very specific format of MultiLineStrings.
        An assert statement is added to help prevent other uses.
    """
    assert all([get_num_points(line) == 2 for line in mls.geoms]), 'Unexpected line length.'
    coords = [get_point(line, 0) for line in mls.geoms]
    coords.append(get_point(mls.geoms[-1], 1))
    return LineString(coords)


geometry1 = LineString([[0, 0], [1, 0], [2, 0], [3, 0]])
geometry2 = LineString([[4, 0], [3, 0], [2, 0], [1, 0]])

overlap_geometry = intersection(geometry1, geometry2)

# Convert MultiLineString to LineString
if isinstance(overlap_geometry, MultiLineString):
    overlap_geometry = ConvertToLineString(overlap_geometry)

print(overlap_geometry)
