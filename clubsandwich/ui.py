import weakref
from contextlib import contextmanager
from math import floor

from bearlibterminal import terminal

from .blt_state import blt_state
from .geom import Point, Rect, Size


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


class View:
  def __init__(self, frame=None, subviews=None):
    self.superview = lambda: None
    self.needs_layout = True
    self._frame = frame or Rect(Point(0, 0), Size(0, 0))
    self._bounds = self.frame.with_origin(Point(0, 0))
    self.subviews = []
    self.add_subviews(subviews or [])
    self.is_first_responder = False

  ### core api ###

  def set_needs_layout(self, val):
    self.needs_layout = val

  def add_subviews(self, subviews):
    for v in subviews:
      v.superview = weakref.ref(self)
    self.subviews.extend(subviews)

  def remove_subviews(self, subviews):
    for v in subviews:
      v.superview = lambda: None
    self.subviews = [v for v in self.subviews if v not in subviews]

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

  ### bounds, frame ###

  @property
  def intrinsic_size(self):
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
    self.set_needs_layout(True)

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
    self.set_needs_layout(True)

  ### responder chain, input ###

  @property
  def can_become_first_responder(self):
    return False

  def become_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = True

  def unbecome_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = False

  def terminal_read(self, val):
    pass

  ### tree traversal ###

  @property
  def leftmost_leaf(self):
    if self.subviews:
      return self.subviews[0].leftmost_leaf
    else:
      return self

  @property
  def postorder_traversal(self):
    for v in self.subviews:
      yield from v.postorder_traversal
    yield self


class FirstResponderContainerView(View):
  """Must be registered on the scene as terminal reader to work."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if len(self.subviews) != 1:
      raise ValueError(
        "FirstResponderContainerView must have exactly one subview.")
    self.first_responder = None
    self.find_next_responder()

  @property
  def intrinsic_size(self):
    return self.subviews[0].intrinsic_size

  def layout_subviews(self):
    self.subviews[0].frame = self.frame

  def find_next_responder(self):
    if self.first_responder:
      self.first_responder.unbecome_first_responder()
    existing_responder = self.first_responder or self.leftmost_leaf
    all_responders = [v for v in self.postorder_traversal if v.can_become_first_responder]
    try:
      i = all_responders.index(existing_responder)
      if i == len(all_responders) - 1:
        self.first_responder = all_responders[0]
      else:
        self.first_responder = all_responders[i + 1]
    except ValueError:
      self.first_responder = all_responders[0] if all_responders else None

    if self.first_responder:
      self.first_responder.become_first_responder()

  def find_prev_responder(self):
    if self.first_responder:
      self.first_responder.unbecome_first_responder()
    existing_responder = self.first_responder or self.leftmost_leaf
    all_responders = [v for v in self.postorder_traversal if v.can_become_first_responder]
    try:
      i = all_responders.index(existing_responder)
      if i == 0:
        self.first_responder = all_responders[-1]
      else:
        self.first_responder = all_responders[i - 1]
    except ValueError:
      self.first_responder = all_responders[-1] if all_responders else None

    if self.first_responder:
      self.first_responder.become_first_responder()

  def terminal_read(self, val):
    if val == terminal.TK_TAB:
      if blt_state.shift:
        self.find_prev_responder()
      else:
        self.find_next_responder()
    elif self.first_responder:
      self.first_responder.terminal_read(val)



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
  def __init__(self, font, text, color_fg='#ffffff', color_bg=None):
    super().__init__()
    self.font = font
    self.figlet_text = None
    self.text = text
    self.color_fg = color_fg
    self.color_bg = color_bg

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
    with temporary_color(self.color_fg, self.color_bg):
      terminal.print(self.frame.origin.x, self.frame.origin.y, self.figlet_text)


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

  def draw(self):
    with temporary_color(self.color_fg, self.color_bg):
      terminal.print(self.frame.origin.x, self.frame.origin.y, self.text)


class ButtonView(View):
  def __init__(self, text, callback):
    self.label_view = LabelView(text)
    super().__init__(subviews=[self.label_view])
    self.callback = callback

  def set_needs_layout(self, val):
    self.label_view.set_needs_layout(val)

  def draw(self):
    if self.is_first_responder:
      self.label_view.color_fg = '#000000'
      self.label_view.color_bg = '#ffffff'
    else:
      self.label_view.color_fg = '#ffffff'
      self.label_view.color_bg = '#000000'
    super().draw()

  @property
  def text(self):
    return self.label_view.text

  @text.setter
  def text(self, new_value):
    self.label_view.text = text

  @property
  def intrinsic_size(self):
    return self.label_view.intrinsic_size

  def layout_subviews(self):
    self.label_view.frame = self.frame

  @property
  def can_become_first_responder(self):
    return True

  def terminal_read(self, val):
    if val == terminal.TK_ENTER:
      self.callback()