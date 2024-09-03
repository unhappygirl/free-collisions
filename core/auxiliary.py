# functions for support

from . import np


def ranges_overlap(ranges):
    # Unpack the ranges
    (min1, max1), (min2, max2) = ranges
    
    # Check if ranges overlap or touch (inclusive)
    return not (max1 < min2 or max2 < min1)


def min_max(l: list):
    return min(l), max(l)

def distance(p1, p2):
    p1_to_p2 = p1.position - p2.position
    _distance = np.linalg.norm(p1_to_p2)
    return _distance


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
