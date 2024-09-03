from . import *
from .auxiliary import normalize_vector, rotate_around
from . import math

BASIS = [np.array((1.0, 0.0)), np.array((0.0, 1.0))]
ORIGIN = np.zeros(2)


class Line:
    def __init__(self, direction, point) -> None:
        self.known_point = np.array(point)
        self.direction = np.array(direction)
        self.direction = normalize_vector(self.direction)
        self.line_function = lambda k: self.known_point + k * self.direction

    def find_y(self, x):
        k = (x - self.known_point[0]) / self.direction[0]
        _, fy = self.line_function(k)
        return fy

    def find_x(self, y):
        k = k = (y - self.known_point[1]) / self.direction[1]
        fx, _ = self.line_function(k)
        return fx

    def rotate(self, a):
        self.direction = rotate_around(a, rp=ORIGIN, p=self.direction)

    def translate(self, tvec):
        self.known_point += tvec


class LineSegment(Line):
    def __init__(self, p1, p2):
        self.p1, self.p2 = np.array(p1), np.array(p2)
        self.segment = self.p2 - self.p1
        known_point = p1
        super().__init__(direction=self.segment, point=known_point)
        self.length = np.linalg.norm(self.segment)
        self.normals = self.find_normals()

    def find_normals(self):
        dx, dy = self.segment
        nx = -dy / self.length
        ny = dx / self.length
        n1 = np.array((nx, ny))
        return n1, -n1


class Circle:
    pass


class SimpleConvexPolygon:
    def __init__(self, points, sides) -> None:
        self.points = list(points)
        self.side_indices = sides
        self.sides = len(self.side_indices)
        self.fetch_side = lambda t: (self.points[t[0]], self.points[t[1]])
        self.segments = list()
        self.outnormals = list()  # consider renaming
        self.center = (
            np.array([sum(p[0] for p in self.points), sum(p[1] for p in self.points)])
            / self.sides
        )
        self.init_segments()

    def init_segments(self):
        for i in range(self.sides):
            side_points = self.get_nth_side_points(i)
            segment = LineSegment(*side_points)
            self.segments.append(segment)
            ctop = segment.p1 - self.center
            n1, n2 = segment.normals
            outnormal = n1 if n1.dot(ctop) > 0 else n2
            self.outnormals.append(outnormal)

    @classmethod
    def generate_n_polygon(cls, n, r=1.0, center=(0, 0)):
        generated = object.__new__(cls)
        step = 2 * math.pi / n
        points = [
            (center[0] + r * np.sin(i * step), center[1] + r * np.cos(i * step))
            for i in range(n)
        ]
        sides = [(i, (i + 1) % n) for i in range(n)]
        generated.__init__(points, sides)
        return generated

    def get_nth_side_points(self, n):
        side_indices = self.side_indices[n]
        return self.fetch_side(side_indices)

    def rotate(self, a, point):
        new_points = []
        for p in self.points:
            new_points.append(rotate_around(a, rp=point, p=p))
        self.__init__(new_points, sides=self.sides)


def update_structure(structre, reinitialize=False, **kwargs):
    if reinitialize:
        return structre.__init__(**kwargs)
    attrs = structre.__dict__
    for key in kwargs:
        attrs[key] = kwargs[key]
    structre.__init__()
