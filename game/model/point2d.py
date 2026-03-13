class Point2D:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point2D):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return 31 * self.x + self.y

    def __repr__(self):
        return f"Point2D[x={self.x}, y={self.y}]"

    def copy(self):
        return Point2D(self.x, self.y)

    def manhattan_distance(self, other: "Point2D") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)
