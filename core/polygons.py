from .lines import LineCollisions
from .structures import SimpleConvexPolygon, Line, LineSegment
from . import np
from .auxiliary import min_max, ranges_overlap, are_collinear


class SimpleConvexPolygonCollisions:
    EDGE_TO_EDGE = 1
    POINT_TO_EDGE = 2
    POINT_TO_POINT = 3
    
    @staticmethod
    def polygon_point(polygon: SimpleConvexPolygon, point):
        for i, ls in enumerate(polygon.segments):
            p1 = ls.p1
            outnormal = polygon.outnormals[i]
            p1top = point - p1
            if p1top.dot(outnormal) > 0:
                return False

        return True

    @staticmethod
    def polygon_line(polygon: SimpleConvexPolygon, line: Line):
        intersections = []
        for ls in polygon.segments:
            intersection = LineCollisions.segment_line(ls, line)
            if isinstance(intersection, np.ndarray):
                intersections.append(intersection)
        return intersections

    @staticmethod
    def polygon_polygon_SAT(poly1: SimpleConvexPolygon, poly2: SimpleConvexPolygon):
        polygons = poly1, poly2
        tested_normals, all_ranges = [], []

        for n in sum(map(lambda p: p.outnormals, polygons), start=[]):
            checked = False
            for t in tested_normals:
                if are_collinear(t, n):
                    checked = True
            if checked:
                continue
            ranges = []
            for poly in polygons:
                products = [n.dot(p) for p in poly.points]
                ranges.append(min_max(products))
            if not ranges_overlap(ranges):
                return False
            all_ranges.append(ranges)
            tested_normals.append(n)

        return True

    @staticmethod
    def SAT_details(ranges: list):
        pass
