import pygame

from core.structures import *
from core import logger, console_handler
from core.lines import *
from core.polygons import *


from logging import DEBUG
import itertools

console_handler.setLevel(DEBUG)


CIRCLE_RADIUS = 6


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
    if axis:
        pygame.draw.circle(pysurface, colors["magenta"], ctps(ax, w, h), CIRCLE_RADIUS)
        pygame.draw.circle(pysurface, colors["magenta"], ctps(ay, w, h), CIRCLE_RADIUS)
    try:
        pygame.draw.line(pysurface, color, ctps(p1, w, h), ctps(p2, w, h))
    except TypeError:
        logger.debug(f"error at with points: {ctps(p1, w, h), ctps(p2, w, h)}")


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

    def cartesian_to_mine(self, point):
        return cartesian_to_pygame_screen(point, *self.size)

    def draw_axes(self):
        w, h = self.size

        cx = w // 2
        cy = h // 2

        # Draw X and Y axes
        pygame.draw.line(self.screen, colors["white"], (0, cy), (w, cy), 2)  # X axis
        pygame.draw.line(self.screen, colors["white"], (cx, 0), (cx, h), 2)  # Y axis


class TestController:
    collision_functions = {
        frozenset(
            {SimpleConvexPolygon, Line}
        ): SimpleConvexPolygonCollisions.polygon_line,
        frozenset(
            {SimpleConvexPolygon, LineSegment}
        ): SimpleConvexPolygonCollisions.polygon_line,
        frozenset(
            {SimpleConvexPolygon, SimpleConvexPolygon}
        ): SimpleConvexPolygonCollisions.polygon_polygon_SAT,
        frozenset({LineSegment, Line}): LineCollisions.segment_line,
        frozenset({LineSegment, LineSegment}): LineCollisions.segment_segment,
        frozenset({Line, Line}): LineCollisions.line_line,
        frozenset({Line, LineSegment}): LineCollisions.segment_line,
        frozenset(
            {Circle, Line}
        ): None,  # Placeholder as Circle handling isn't implemented
        frozenset(
            {Circle, LineSegment}
        ): None,  # Placeholder as Circle handling isn't implemented
        frozenset(
            {Circle, SimpleConvexPolygon}
        ): None,  # Placeholder as Circle handling isn't implemented
        frozenset(
            {Circle, Circle}
        ): None,  # Placeholder as Circle handling isn't implemented
    }

    def __init__(self, structures, testframe: TestFrame) -> None:
        self.structures = structures
        self.testframe = testframe

    def collision_testing(self):
        for comb in itertools.combinations(self.structures):
            func = self.collision_functions[frozenset(map(type, comb))]
            s1, s2 = comb
            try:
                func(s1, s2)
            except:
                func(s2, s1)

    def draw_structures(self):
        for s in self.structures:
            pass


def main():
    import random

    a = TestFrame((800, 800))
    myline = Line((1.0, 1.0), (0.0, 0.0))
    mypoly = SimpleConvexPolygon.generate_n_polygon(
        n=random.randint(3, 10), r=random.randint(50, 300)
    )
    clock = pygame.time.Clock()
    while True:
        pygame.event.pump()
        ins = SimpleConvexPolygonCollisions.polygon_line(mypoly, myline)
        a.draw_axes()
        draw_line(myline, a.screen, color=colors["cyan"])
        draw_polygon(mypoly, a.screen)
        for i in ins:
            pygame.draw.circle(
                a.screen, colors["green"], a.cartesian_to_mine(i), CIRCLE_RADIUS
            )
        pygame.display.flip()
        mpos = np.array(
            pygame_screen_to_cartesian(pygame.mouse.get_pos(), *a.screen.get_size())
        )
        if pygame.mouse.get_pressed()[0]:
            myline.translate(mpos - myline.known_point)
        else:
            update_structure(
                myline,
                reinitialize=True,
                point=(0.0, 0.0),
                direction=mpos - myline.direction,
            )

        a.clear_screen()
        clock.tick(60)

        if pygame.event.get() == pygame.QUIT:
            break


if __name__ == "__main__":
    main()
