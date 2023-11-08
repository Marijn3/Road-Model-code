import shapely


def ExtractLineStringCoordinates(ls: shapely.LineString) -> list[list[float, float]]:
    return list(ls.coords)


def ExtractPointCoordinates(point: shapely.Point) -> list[float, float]:
    return list(point.coords)


def CheckLineInExtent(lg: list[list[float, float]], extent) -> bool:
    for (x, y) in lg:
        if CheckPointInExtent(x, y, extent):
            return True
    return False


def CheckPointInExtent(x, y, extent):
    xmin, ymin, xmax, ymax = extent
    return xmin <= x <= xmax and ymin <= y <= ymax
