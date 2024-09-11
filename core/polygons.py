from .lines import LineCollisions
from ._types import Collision
from ._types import SimpleConvexPolygon, Line, LineSegment
from . import logger, np
from .auxiliary import (
    min_max,
    ranges_overlap,
    range_length,
    are_collinear,
    overlap_range,
)


class SimpleConvexPolygonCollisions:
    EDGE_TO_EDGE = 0
    POINT_TO_EDGE = 1
    POINT_TO_POINT = 31

    @staticmethod
    def polygon_point(polygon: SimpleConvexPolygon, point):
        for i, ls in enumerate(polygon.segments):
            p1 = ls.p1
            outnormal = polygon.outnormals[i]
            p1top = point - p1
            if p1top.dot(outnormal) > 0:
                return Collision(False)

        return Collision(True)

    @staticmethod
    def polygon_line(polygon: SimpleConvexPolygon, line: Line):
        intersections = []
        for ls in polygon.segments:
            intersection = LineCollisions.segment_line(ls, line)
            if intersection:
                intersections.append(intersection.point)
        return Collision(intersections, bool(intersections))

    @staticmethod
    def polygon_polygon_SAT(poly1: SimpleConvexPolygon, poly2: SimpleConvexPolygon):
        polygons = poly1, poly2
        data = []

        for n in poly1.outnormals + poly2.outnormals:
            for *_, n_ in data:
                if are_collinear(n, n_):
                    break
            else:
                extremes = []
                for poly in polygons:
                    products = [n.dot(p) for p in poly.points]
                    extremes.append(min_max(products))
                if ranges_overlap(extremes):
                    data.append([overlap_range(*extremes), n])
                else:
                    return Collision(False)

        details = __class__.SAT_details(data, poly1, poly2)
        return Collision(True, details)

    @staticmethod
    def polygon_polygon_GJK(poly1: SimpleConvexPolygon, poly2: SimpleConvexPolygon):
        pass

    # decided to separate calculating other properties of the collision
    @staticmethod
    def SAT_details(data: list, poly1, poly2):
        min_overlap = min(data, key=lambda d: range_length(d[0]))
        min_range, pnormal = min_overlap
        collision_structures = []
        products1 = [pnormal.dot(p) for p in poly1.points]
        products2 = [pnormal.dot(p) for p in poly2.points]
        print(products1, products2)
        for d in min_range:
            pack = (products1, poly1) if d in products1 else (products2, poly2)
            products, poly = pack
            indices = [idx for idx, d_ in enumerate(products) if np.isclose(d_, d, 0.01)]
            if len(indices) == 2:
                points = map(lambda idx: poly.points[idx], indices)
                collision_structures.append(LineSegment(*points))
            else:
                collision_structures.append(poly.points[indices[0]])

        s1, s2 = collision_structures
        cpoint = s1 if type(s2) is LineSegment else s2
        if type(cpoint) is LineSegment:
            collision_type = __class__.EDGE_TO_EDGE
            cpoint = None
        else:
            collision_type = __class__.POINT_TO_EDGE
        logger.debug(
            f"cpoint: {cpoint}, s1: {type(s1)}, s2: {type(s2)}, min_range: {min_range}, pnormal: {pnormal}, indices: {indices}"
        )

        return {
            "point": cpoint,
            "normal": pnormal,
            "collision_structures": collision_structures,
            "penetration_vector": range_length(min_range) * pnormal,
        }

    @staticmethod
    def polygon_polygon_points(poly1: SimpleConvexPolygon, poly2: SimpleConvexPolygon):
        points = [[], []]
        for p1 in poly1.points:
            if __class__.polygon_point(poly2, p1):
                points[0].append(p1)
        for p2 in poly2.points:
            if __class__.polygon_point(poly1, p2):
                points[1].append(p2)
        return points
