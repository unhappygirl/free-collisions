# functions for support

from . import np, math


def ranges_overlap(ranges):
    # Unpack the ranges
    (min1, max1), (min2, max2) = ranges

    # Check if ranges overlap or touch (inclusive)
    return not (max1 < min2 or max2 < min1)


def overlap_range(range1, range2):
    min1, max1 = range1
    min2, max2 = range2

    # Find the maximum of the lower bounds and the minimum of the upper bounds
    lb = max(min1, min2)
    ub = min(max1, max2)

    # If the bounds overlap, return the overlapping range
    if lb <= ub:
        return lb, ub
    return


def range_length(range):
    return abs(range[1] - range[0])


def min_max(l: list, key=None):
    return min(l, key=key), max(l, key=key)


def distance(p1, p2):
    p1_to_p2 = p1.position - p2.position
    _distance = np.linalg.norm(p1_to_p2)
    return _distance


def distance_to_line(p: np.ndarray, direction: np.ndarray, known_point: np.ndarray):
    x = (p - known_point).dot(direction)
    projection = x * direction + known_point
    return np.linalg.norm(projection - p)


def are_collinear(v1, v2):
    v13 = np.array(list(v1) + [0])
    v23 = np.array(list(v2) + [0])
    cross = np.cross(v13, v23)
    return not cross.any()


def normalize_vector(v: np.ndarray):
    mag = np.linalg.norm(v)
    return v / mag


def vector_projection(v1: np.ndarray, v2: np.ndarray):
    v2mag = np.linalg.norm(v2)
    uv2 = v2 / v2mag
    return v1.dot(uv2) * uv2


def rotation_matrix_2d(angle):
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])


def rotate_around(angle, rp, p):
    p -= rp
    p = p.dot(rotation_matrix_2d(angle))
    p += rp
    return p
