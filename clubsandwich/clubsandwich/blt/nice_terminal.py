from bearlibterminal import terminal as _terminal
from clubsandwich.geom import Point, Rect

class NiceTerminal:
  """
  Like bearlibterminal.terminal, but some functions support geom.py data
  structures
  """
  def __getattr__(self, k):
    return getattr(_terminal, k)

  def clear_area(self, *args):
    if args and isinstance(args[0], Rect):
      return _terminal.clear_area(
        args[0].origin.x, args[0].origin.y,
        args[0].size.width, args[0].size.height)
    else:
      return _terminal.clear_area(*args)

  def crop(self, *args):
    if args and isinstance(args[0], Rect):
      return _terminal.crop(
        args[0].origin.x, args[0].origin.y,
        args[0].size.width, args[0].size.height)
    else:
      return _terminal.crop(*args)

  def print(self, *args):
    if isinstance(args[0], Point):
      return _terminal.print(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.print(*args)

  def printf(self, *args):
    if isinstance(args[0], Point):
      return _terminal.printf(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.printf(*args)

  def put(self, *args):
    if isinstance(args[0], Point):
      return _terminal.put(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.put(*args)

  def pick(self, *args):
    if isinstance(args[0], Point):
      return _terminal.pick(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.pick(*args)

  def pick_color(self, *args):
    if isinstance(args[0], Point):
      return _terminal.pick_color(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.pick_color(*args)

  def pick_bkcolor(self, *args):
    if isinstance(args[0], Point):
      return _terminal.pick_bkcolor(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.pick_bkcolor(*args)

  def put_ext(self, *args):
    if isinstance(args[0], Point):
      return _terminal.put_ext(args[0].x, args[0].y, args[1].x, args[1].y, *args[2:])
    else:
      return _terminal.put_ext(*args)

  def read_str(self, *args):
    if isinstance(args[0], Point):
      return _terminal.read_str(args[0].x, args[0].y, *args[1:])
    else:
      return _terminal.read_str(*args)

terminal = NiceTerminal()