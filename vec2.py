

class Vec2:

    def __init__(self, *args):
        if hasattr(args[0], "__getitem__"):
            self.data = list(args[0])
        elif len(args) == 2:
            self.data = [x for x in args]
        else:
            raise TypeError("Vec2 unable to accept %s" % args)

    @property
    def x(self):
        return self.data[0]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @property
    def y(self):
        return self.data[1]

    @y.setter
    def y(self, value):
        self.data[1] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        return str(self.data)
    __repr__ = __str__

    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self[0] + other[0], self[1] + other[1])
        else:
            return Vec2(self[0] + other, self[1] + other)
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self[0] - other[0], self[1] - other[1])
        else:
            return Vec2(self[0] - other, self[1] - other)

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self[0] * other[0], self[1] * other[1])
        else:
            return Vec2(self[0] * other, self[1] * other)
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self[0] / other[0], self[1] / other[1])
        else:
            return Vec2(self[0] / other, self[1] / other)

    def __eq__(self, other):
        if self[0] == other[0] and self[1] == other[1]:
            return True
        return False

    def copy(self):
        return Vec2(self.data[:])

    def render(self):
        return int(round(self[0])), int(round(self[1]))
