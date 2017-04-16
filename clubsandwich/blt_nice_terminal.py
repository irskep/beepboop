from bearlibterminal import terminal as _terminal
from .geom import Point, Rect

class NiceTerminal:
  """
  Like bearlibterminal.terminal, but some functions support geom.py data
  structures
  """
  def __getattr__(self, k):
    return getattr(_terminal, k)

  def put(self, *args):
    if isinstance(args[0], Point):
      _terminal.put(args[0].x, args[0].y, *args[1:])
    else:
      _terminal.put(*args)

terminal = NiceTerminal()