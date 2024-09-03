from .structures import Line, LineSegment
from . import *


class LineCollisions:
    @staticmethod
    def line_point(line: Line, point: np.ndarray, atol=2) -> bool:
        # Calculate the difference between the point and a known point on the line
        diff = point - line.known_point
        # Check if the cross product of the difference and line direction is close to zero
        # This determines if the point lies on the line within a tolerance (atol)
        return np.isclose(np.cross(diff, line.direction), 0, atol=atol)

    @staticmethod
    def line_line(line1, line2) -> np.ndarray:
        # Calculate the vector difference between the known points of the two lines
        diff = line2.known_point - line1.known_point
        # Extract the components of the direction vectors for both lines
        sx, sy = line1.direction
        ox, oy = line2.direction
        # Construct a matrix using the direction vectors
        M = np.array([[sx, -ox], [sy, -oy]])
        # Solve the linear system to find the intersection point
        solutions = np.linalg.solve(M, diff)
        # Return the intersection point by evaluating the line function at the solution
        return line1.line_function(solutions[0])
    
    @staticmethod
    def segment_point(line_segment: LineSegment, point) -> bool:
        # Check if the point is on the infinite line defined by the line segment
        on_line = LineCollisions.line_point(line_segment, point)
        if not on_line:
            # Return False if the point is not on the infinite line
            return False

        # Calculate the multiplier of the difference vector
        diff = point - line_segment.p1
        s = line_segment.segment
        k = s.dot(diff)/s.dot(s)
        # Check if the difference lies within the bounds of the segment's length
        if 0 <= k <= 1:
            logger.debug(f"inside class {__class__}, function segment_point: k is  {k}")
        return 0 <= k <= 1

    @staticmethod
    def segment_line(line_segment: LineSegment, line: Line):
        # Get the intersection point of the line that segment lies on and the other line
        intersection = LineCollisions.line_line(line_segment, line)
        if not isinstance(intersection, np.ndarray):
            # Return False if there's no intersection
            return False

        # Check if the intersection point is within the bounds of the line segment
        return (
            intersection
            if __class__.segment_point(line_segment, intersection)
            else None
        )

    @staticmethod
    def segment_segment(ls1, ls2):
        # Get the intersection of two line segments treated as lines
        intersection = __class__.segment_line(ls1, ls2)
        # If the intersection isn't an array (i.e., no valid point), return False
        if not isinstance(intersection, np.ndarray):
            return False
        # Check if the intersection point lies within the bounds of the second segment
        return __class__.segment_point(intersection)
    

