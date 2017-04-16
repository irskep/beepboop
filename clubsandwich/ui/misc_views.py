from .view import View
from contextlib import contextmanager
from math import floor

from ..blt_nice_terminal import terminal
from ..blt_state import blt_state
from ..geom import Point, Rect, Size
from .view import View


@contextmanager
def temporary_color(fg, bg):
  old_fg = blt_state.color
  old_bg = blt_state.bkcolor
  if fg:
    terminal.color(fg)
  if bg:
    terminal.bkcolor(bg)
  yield
  terminal.color(old_fg)
  terminal.bkcolor(old_bg)


class VerticalSplitView(View):
  def __init__(self, *args, ratios=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.ratios = ratios

  def layout_subviews(self):
    sub_height = floor(self.bounds.size.height / len(self.subviews))
    next_y = self.bounds.origin.y
    for i, view in enumerate(self.subviews):
      height = sub_height
      if self.ratios:
        height = self.bounds.size.height * self.ratios[i]

      view.frame = Rect(
        Point(self.bounds.origin.x, next_y),
        Size(self.bounds.size.width, height)).floored
      next_y = view.frame.origin.y + view.frame.size.height

class HorizontalSplitView(View):
  def __init__(self, *args, ratios=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.ratios = ratios

  def layout_subviews(self):
    # TODO: implement ratios like VerticalSplitView
    sub_width = floor(self.bounds.size.width / len(self.subviews))
    for i, view in enumerate(self.subviews):
      view.frame = Rect(
        Point(self.bounds.origin.x + i * sub_width, self.bounds.origin.y),
        Size(sub_width, self.bounds.size.height)).floored


class FillerView(View):
  def __init__(
      self,
      behavior_x='middle', behavior_y='middle',
      inset=None, size=None,
      *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.behavior_x = behavior_x
    self.behavior_y = behavior_y
    self.inset = inset or Size(0, 0)
    self.size = size

  @property
  def behavior_x(self):
    return self._behavior_x

  @behavior_x.setter
  def behavior_x(self, new_value):
    self._behavior_x = self._synonym(new_value)

  @property
  def behavior_y(self):
    return self._behavior_y

  @behavior_y.setter
  def behavior_y(self, new_value):
    self._behavior_y = self._synonym(new_value)

  def _synonym(self, val):
    if val == 'center': return 'middle'
    if val == 'const': return 'constant'
    if val in ('start', 'beginning', 'left', 'top'):
      return 'begin'
    if val in ('finish', 'ending', 'right', 'bottom'):
      return 'end'
    return val

  def layout_subviews(self):
    for view in self.subviews:
      intrinsic_size = self.size or view.intrinsic_size

      x = 0
      if self.behavior_x in ('begin', 'fill', 'constant'):
        x = self.bounds.origin.x + self.inset.width
      elif self.behavior_x == 'middle':
        x = self.bounds.center.x - intrinsic_size.width / 2
      elif self.behavior_x == 'end':
        x = (
          self.bounds.origin.x +
          self.bounds.size.width -
          intrinsic_size.width -
          self.inset.width)

      y = 0
      if self.behavior_y in ('begin', 'fill', 'constant'):
        y = self.bounds.origin.y + self.inset.height
      elif self.behavior_y == 'middle':
        y = self.bounds.center.y - intrinsic_size.height / 2
      elif self.behavior_y == 'end':
        y = (
          self.bounds.origin.y +
          self.bounds.size.height -
          intrinsic_size.height -
          self.inset.height)

      width = view.bounds.size.width
      if self.behavior_x == 'fill':
        width = self.bounds.size.width - self.inset.width * 2
      elif self.behavior_x == 'constant':
        width = self.size.width - self.inset.width * 2
      else:
        width = intrinsic_size.width

      height = view.bounds.size.height
      if self.behavior_y == 'fill':
        height = self.bounds.size.height - self.inset.height * 2
      elif self.behavior_y == 'constant':
        height = self.size.height - self.inset.height * 2
      else:
        height = intrinsic_size.height

      view.frame = Rect(Point(x, y), Size(width, height)).floored


class RectView(View):
  def __init__(self, color_fg='#aaaaaa', color_bg='#000000', *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.color_fg = color_fg
    self.color_bg = color_bg

  def draw(self, ctx):
    with temporary_color(self.color_fg, self.color_bg):
      ctx.clear_area(self.bounds)
      for point in self.bounds.points_top:
        ctx.put(point, '─')
      for point in self.bounds.points_bottom:
        ctx.put(point, '─')
      for point in self.bounds.points_left:
        ctx.put(point, '│')
      for point in self.bounds.points_right:
        ctx.put(point, '│')
      ctx.put(self.bounds.origin, '┌')
      ctx.put(self.bounds.point_top_right, '┐')
      ctx.put(self.bounds.point_bottom_left, '└')
      ctx.put(self.bounds.point_bottom_right, '┘')


class WindowView(RectView):
  def __init__(self, title=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.title_view = FillerView(
        behavior_x='center', behavior_y='top',
        subviews=[
          LabelView(title),
        ])
    
    self.add_subviews([self.title_view])

  def layout_subviews(self):
    super().layout_subviews()
    for sv in self.subviews:
      if sv == self.title_view:
        sv.frame = self.bounds.with_size(Size(self.bounds.size.width, 1))
      else:
        sv.frame = self.bounds.with_inset(Size(1, 1))


class CenteringView(View):
  def layout_subviews(self):
    center = self.bounds.center
    for view in self.subviews:
      view.frame = view.bounds.with_origin(center - intrinsic_size / 2).floored


class ImageView(View):
  def __init__(self, text, color_fg='#ffffff', color_bg=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.text = text
    self.color_fg = color_fg
    self.color_bg = color_bg

  @property
  def intrinsic_size(self):
    height = 0
    width = 0
    for line in self.text.splitlines():
      height += 1
      width = max(width, len(line))
    return Size(width, height)

  def draw(self, ctx):
    with temporary_color(self.color_fg, self.color_bg):
      ctx.print(self.bounds.origin, self.text)


class LabelView(View):
  def __init__(self, text, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.text = text
    self.color_fg = '#ffffff'
    self.color_bg = None

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

  def draw(self, ctx):
    with temporary_color(self.color_fg, self.color_bg):
      ctx.print(self.bounds.origin, self.text)

  def debug_string(self):
    return super().debug_string() + ' ' + repr(self.text)


class ButtonView(View):
  def __init__(self, text, callback, *args, **kwargs):
    self.label_view = LabelView(text, *args, **kwargs)
    super().__init__(subviews=[self.label_view], *args, **kwargs)
    self.callback = callback

  def set_needs_layout(self, val):
    super().set_needs_layout(val)
    self.label_view.set_needs_layout(val)

  def did_become_first_responder(self):
      self.label_view.color_fg = '#000000'
      self.label_view.color_bg = '#ffffff'

  def did_resign_first_responder(self):
      self.label_view.color_fg = '#ffffff'
      self.label_view.color_bg = '#000000'

  @property
  def text(self):
    return self.label_view.text

  @text.setter
  def text(self, new_value):
    self.label_view.text = new_value

  @property
  def intrinsic_size(self):
    return self.label_view.intrinsic_size

  def layout_subviews(self):
    super().layout_subviews()
    self.label_view.frame = self.bounds

  @property
  def can_did_become_first_responder(self):
    return True

  def terminal_read(self, val):
    if val == terminal.TK_ENTER:
      self.callback()
      return True