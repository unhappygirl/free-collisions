import pygame

from core._types import *
from core import logger, console_handler
from core.lines import *
from core.polygons import *
from numpy.random import random_sample, randint
from logging import DEBUG
import itertools

console_handler.setLevel(DEBUG)


CIRCLE_RADIUS = 5


colors = {
    "white": "#FFFFFF",
    "black": "#000000",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "gray": "#808080",
    "light_gray": "#D3D3D3",
    "dark_gray": "#A9A9A9",
    "orange": "#FFA500",
    "purple": "#800080",
    "pink": "#FFC0CB",
    "brown": "#A52A2A",
}


def swap(t: tuple):
    t = (t[1], t[0])
    return t


def cartesian_to_pygame_screen(cartesian_point, sw, sh):
    x, y = cartesian_point
    sx = int(sw / 2 + x)
    sy = int(sh / 2 - y)

    return (sx, sy)


def pygame_screen_to_cartesian(screen_point, sw, sh):
    sx, sy = screen_point
    x = sx - sw / 2
    y = sh / 2 - sy

    return (x, y)


def draw_point(p: np.ndarray, pysurface: pygame.Surface):
    pygame.draw.circle(
        pysurface,
        colors["orange"],
        cartesian_to_pygame_screen(p, *pysurface.get_size()),
        CIRCLE_RADIUS,
    )


def draw_polygon(
    poly: SimpleConvexPolygon, pysurface: pygame.Surface, color=colors["white"]
):
    w, h = pysurface.get_size()
    adapted = map(lambda p: cartesian_to_pygame_screen(p, w, h), poly.points)
    pygame.draw.polygon(pysurface, color, list(adapted), width=3)


def draw_line(l: Line, pysurface: pygame.Surface, color, axis=False):
    ctps = cartesian_to_pygame_screen
    w, h = pysurface.get_size()
    p1 = (w // 2, l.find_y(w // 2))
    p2 = (-w // 2, l.find_y(-w // 2))
    ay = (0, l.find_y(0))
    ax = (l.find_x(0), 0)
    try:
        pygame.draw.line(pysurface, color, ctps(p1, w, h), ctps(p2, w, h), width=1)
    except TypeError:
        logger.debug(f"error at with points: {ctps(p1, w, h), ctps(p2, w, h)}")
    if axis:
        pygame.draw.circle(pysurface, colors["magenta"], ctps(ax, w, h), CIRCLE_RADIUS)
        pygame.draw.circle(pysurface, colors["magenta"], ctps(ay, w, h), CIRCLE_RADIUS)


def draw_ls(ls: LineSegment, pysurface: pygame.Surface, color):
    ctps = cartesian_to_pygame_screen
    w, h = pysurface.get_size()
    pygame.draw.line(pysurface, color, ctps(ls.p1, w, h), ctps(ls.p2, w, h))
    pygame.draw.circle(pysurface, colors["magenta"], ctps(ls.p1, w, h), CIRCLE_RADIUS)
    pygame.draw.circle(pysurface, colors["magenta"], ctps(ls.p2, w, h), CIRCLE_RADIUS)


class TestFrame:
    def __init__(self, size) -> None:
        self.size = size
        self.screen = pygame.display.set_mode(self.size)

    def clear_screen(self):
        self.screen.fill(colors["white"])
        self.screen.fill(colors["black"])

    def draw_axes(self):
        w, h = self.size

        cx = w // 2
        cy = h // 2

        # Draw X and Y axes
        pygame.draw.line(self.screen, colors["white"], (0, cy), (w, cy), 2)  # X axis
        pygame.draw.line(self.screen, colors["white"], (cx, 0), (cx, h), 2)  # Y axis


class TestController:
    collision_functions = {
        (SimpleConvexPolygon, Line): SimpleConvexPolygonCollisions.polygon_line,
        (SimpleConvexPolygon, LineSegment): SimpleConvexPolygonCollisions.polygon_line,
        (
            SimpleConvexPolygon,
            SimpleConvexPolygon,
        ): SimpleConvexPolygonCollisions.polygon_polygon_SAT,
        (LineSegment, Line): LineCollisions.segment_line,
        (LineSegment, LineSegment): LineCollisions.segment_segment,
        (Line, Line): LineCollisions.line_line,
        (Circle, Line): None,  # Placeholder as Circle handling isn't implemented
        (Circle, LineSegment): None,  # Placeholder as Circle handling isn't implemented
        (
            Circle,
            SimpleConvexPolygon,
        ): None,  # Placeholder as Circle handling isn't implemented
        (Circle, Circle): None,  # Placeholder as Circle handling isn't implemented
    }

    def random_lines(self, k):
        lines = []
        for _ in range(k):
            direction = random_sample(2)
            point = random_sample(2) * (self.testframe.size[0] / 2)
            lines.append(Line(direction=direction, point=point))
        return lines

    def random_polygons(self, k):
        polygons = []
        for _ in range(k):
            poly = SimpleConvexPolygon.generate_n_polygon(
                n=randint(3, 6),
                r=randint(40, 100),
                center=random_sample(2) * (self.testframe.size[0] / 2),
            )
            polygons.append(poly)
        return polygons

    def __init__(self, structures, testframe: TestFrame) -> None:
        self.structures = structures
        self.testframe = testframe
        self.drawers = {
            np.ndarray: lambda p: draw_point(p, self.testframe.screen),
            Line: lambda line: draw_line(
                line, self.testframe.screen, colors["cyan"], axis=False
            ),
            LineSegment: lambda ls: draw_ls(ls, self.testframe.screen, colors["cyan"]),
            SimpleConvexPolygon: lambda poly: draw_polygon(
                poly, self.testframe.screen, colors["red"]
            ),
        }

    def draw_collision(self, collision: Collision):
        # logger.debug(f"drawing collision object {collision}")
        if collision.point is not None:
            self.drawers[np.ndarray](collision.point)
            if collision.penetration_vector is not None:
                try:
                    pygame.draw.line(
                        self.testframe.screen,
                        colors["yellow"],
                        cartesian_to_pygame_screen(
                            collision.point, *self.testframe.size
                        ),
                        cartesian_to_pygame_screen(
                            collision.point + collision.penetration_vector,
                            *self.testframe.size,
                        ),
                    )
                except:
                    return
        if collision.points is not None:
            for p in collision.points:
                self.drawers[np.ndarray](p)

    def collision_testing(self):
        for comb in itertools.combinations(self.structures, 2):
            args = tuple(map(type, comb))
            if args not in self.collision_functions:
                comb = swap(comb)
                args = swap(args)
            func = self.collision_functions[args]
            c = func(*comb)
            if c:
                # logger.debug(f"collision found for {args}!")
                self.draw_collision(c)

    def draw_structures(self):
        for s in self.structures:
            func = self.drawers[type(s)]
            func(s)

    def draw_all(self):
        self.testframe.draw_axes()
        self.draw_structures()
        self.collision_testing()

    def handle_input(self, mstate, kstate):
        mpos, pressed = mstate
        if pressed[0]:
            for s in self.structures:
                t = type(s)
                if t is SimpleConvexPolygon:
                    if SimpleConvexPolygonCollisions.polygon_point(s, mpos):
                        s.translate(mpos - s.center)
                        return
                elif t is Line:
                    c = LineCollisions.line_point(s, mpos, atol=50)
                    if c:
                        s.translate(mpos - s.known_point)
                        return

    def mainloop(self, framerate):
        clock = pygame.time.Clock()
        while True:
            pygame.event.pump()
            mstate = (
                np.array(
                    pygame_screen_to_cartesian(
                        pygame.mouse.get_pos(), *self.testframe.size
                    )
                ),
                pygame.mouse.get_pressed(),
            )
            kstate = pygame.key.get_pressed()
            self.handle_input(mstate, kstate)
            self.draw_all()
            pygame.display.flip()
            clock.tick(framerate)
            self.testframe.clear_screen()


def main():
    mytestframe = TestFrame((800, 800))
    mycontroller = TestController(
        [],
        mytestframe,
    )
    mycontroller.structures += mycontroller.random_polygons(10)
    mycontroller.structures += mycontroller.random_lines(0)

    mycontroller.mainloop(framerate=60)


if __name__ == "__main__":
    main()
