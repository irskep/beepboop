from .view import View
from contextlib import contextmanager
from math import floor

from ..blt_nice_terminal import terminal
from ..blt_state import blt_state
from ..geom import Point, Rect, Size
from .view import View
from .layout_options import LayoutOptions


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
  def __init__(self, title=None, *args, subviews=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.title_view = LabelView(title, layout_options=LayoutOptions.row_top(1))
    self.content_view = View(
      subviews=subviews,
      layout_options=LayoutOptions(top=1, right=1, bottom=1, left=1))
    self.add_subviews([self.title_view, self.content_view])


class LabelView(View):
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
      ctx.print((self.bounds.size / 2 - self.intrinsic_size / 2).floored, self.text)

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