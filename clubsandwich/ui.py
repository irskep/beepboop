from math import floor

from bearlibterminal import terminal

from .geom import Point, Rect, Size


class View:
  def __init__(self, frame=None, subviews=None):
    self.needs_layout = True
    self._frame = frame or Rect(Point(0, 0), Size(0, 0))
    self._bounds = self.frame.with_origin(Point(0, 0))
    self.subviews = subviews or []

  def draw(self):
    for view in self.subviews:
      view.draw()

  def perform_layout(self):
    if self.needs_layout:
      self.layout_subviews()
      self.needs_layout = False
    for view in self.subviews:
      view.perform_layout()

  def layout_subviews(self):
    pass

  @property
  def intrins_size(self):
    return Point(0, 0)

  @property
  def frame(self):
    return self._frame

  @frame.setter
  def frame(self, new_value):
    if new_value == self._frame:
      return
    self._frame = new_value
    self._bounds = new_value.with_origin(Point(0, 0))
    self.needs_layout = True

  @property
  def bounds(self):
    return self._bounds

  @bounds.setter
  def bounds(self, new_value):
    if new_value.origin != Point(0, 0):
        raise ValueError("Bounds is always anchored at (0, 0)")
    if new_value == self._bounds:
      return
    self._bounds = new_value
    self._frame = self._frame.with_size(new_value.size)
    self.needs_layout = True


class VerticalSplitView(View):
  def layout_subviews(self):
    sub_height = floor(self.bounds.size.height / len(self.subviews))
    for i, view in enumerate(self.subviews):
      view.frame = Rect(
        Point(self.frame.origin.x, self.frame.origin.y + i * sub_height),
        Size(self.bounds.size.width, sub_height))


class HorizontalSplitView(View):
  def layout_subviews(self):
    sub_width = floor(self.bounds.size.width / len(self.subviews))
    for i, view in enumerate(self.subviews):
      view.frame = Rect(
        Point(self.frame.origin.x + i * sub_width, self.frame.origin.y),
        Size(sub_width, self.bounds.size.height))


class CenteringView(View):
  def layout_subviews(self):
    center = self.frame.center
    for view in self.subviews:
      view.frame = view.bounds.with_origin(center - view.intrinsic_size / 2).floored


class FigletView(View):
  def __init__(self, font, text):
    super().__init__()
    self.font = font
    self.figlet_text = None
    self.text = text

  @property
  def text(self):
    return self._text

  @text.setter
  def text(self, new_value):
    self._text = new_value
    self.figlet_text = self.font.renderText(new_value)

  @property
  def intrinsic_size(self):
    height = 0
    width = 0
    for line in self.figlet_text.splitlines():
      height += 1
      width = max(0, len(line))
    return Size(width, height)

  def draw(self):
    terminal.print(self.frame.origin.x, self.frame.origin.y, self.figlet_text)


class LabelView(View):
  def __init__(self, text, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.text = text

  @property
  def text(self):
    return self._text

  @text.setter
  def text(self, new_value):
    self._text = new_value
    self.bounds = Rect(Point(0, 0), self.intrinsic_size)

  @property
  def intrinsic_size(self):
    return Size(len(self.text), 1)

  def draw(self):
    terminal.print(self.frame.origin.x, self.frame.origin.y, self.text)