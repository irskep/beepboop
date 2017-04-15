from math import floor

class Point:
  __slots__ = ('x', 'y')

  def __init__(self, x=0, y=0):
    super().__init__()
    self.x = x
    self.y = y

  def __eq__(self, other):
    if not isinstance(other, Point):
        return False
    return self.x == other.x and self.y == other.y

  def __repr__(self):
    return 'Point({}, {})'.format(self.x, self.y)

  @property
  def floored(self):
    return self.__class__(floor(self.x), floor(self.y))

  def __add__(self, other):
    return self.__class__(self.x + other.x, self.y + other.y)

  def __mul__(self, other):
    if isinstance(other, Point):
      return self.__class__(self.x * other.x, self.y * other.y)
    else:
      return self.__class__(self.x * other, self.y * other)

  def __sub__(self, other):
    return self + (other * -1)

  def __truediv__(self, other):
    if isinstance(other, Point):
      return self.__class__(self.x / other.x, self.y / other.y)
    else:
      return self.__class__(self.x / other, self.y / other)


class Size(Point):
  def __init__(self, width=0, height=0):
    super().__init__(x=width, y=height)

  @property
  def point(self):
    return Point(self.width, self.height)

  @property
  def width(self):
    return self.x

  @width.setter
  def width(self, value):
    self.x = value

  @property
  def height(self):
    return self.y

  @height.setter
  def height(self, value):
    self.y = value

  def __repr__(self):
    return 'Size({}, {})'.format(self.width, self.height)


class Rect:
  __slots__ = ('origin', 'size')

  def __init__(self, origin=None, size=None):
    super().__init__()
    self.origin = origin or Point()
    self.size = size or Size()

  def __eq__(self, other):
    if not isinstance(other, Rect):
      return False
    return self.origin == other.origin and self.size == other.size

  def __repr__(self):
    return 'Rect({!r}, {!r})'.format(self.origin, self.size)

  @property
  def points(self):
    for x in range(self.origin.x, self.origin.x + self.size.width):
      for y in range(self.origin.y, self.origin.y + self.size.height):
        yield Point(x, y)

  @property
  def floored(self):
    return Rect(self.origin.floored, self.size.floored)

  @property
  def center(self):
    return self.origin + self.size / 2

  def with_origin(self, new_origin):
    return Rect(new_origin, self.size)

  def with_size(self, new_size):
    return Rect(self.origin, new_size)

  def create_centered(self, size):
    return Rect((self.size / 2 - size / 2).point, size)