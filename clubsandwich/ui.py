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
  def __init__(self, frame=None, subviews=None, oninit=None):
    self._superview_weakref = lambda: None
    self.needs_layout = True
    self._frame = frame or Rect(Point(0, 0), Size(0, 0))
    self._bounds = self.frame.with_origin(Point(0, 0))
    self.subviews = []
    self.add_subviews(subviews or [])
    self.is_first_responder = False

    if oninit:
      oninit()

  ### core api ###

  @property
  def superview(self):
    return self._superview_weakref()

  @superview.setter
  def superview(self, new_value):
    if new_value:
      self._superview_weakref = weakref.ref(new_value)
    else:
      self._superview_weakref = lambda: None

  def set_needs_layout(self, val):
    self.needs_layout = val

  def add_subviews(self, subviews):
    for v in subviews:
      v.superview = self
    self.subviews.extend(subviews)
    terminal.clear()

  def remove_subviews(self, subviews):
    for v in subviews:
      v.superview = None
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

  @property
  def can_unbecome_first_responder(self):
    return True

  def become_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = True

  def unbecome_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = False

  @property
  def should_become_first_responder_immediately(self):
    return False

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

  @property
  def ancestors():
    v = self.superview
    while v:
      yield v

  def get_ancestor_matching(self, predicate):
    for ancestor in self.ancestors:
      if predicate(v):
        return v
    return None

  def debug_string(self):
    return '{} {!r}'.format(type(self).__name__, self.frame)

  def debug_print(self, indent=0):
    print(' ' * indent + self.debug_string())
    for sv in self.subviews:
      sv.debug_print(indent + 2)


class FirstResponderContainerView(View):
  """Must be registered on the scene as terminal reader to work."""
  def __init__(self, *args, **kwargs):
    self.first_responder = None
    super().__init__(*args, **kwargs)
    self.first_responder = None
    self.find_next_responder()

  @property
  def intrinsic_size(self):
    return self.subviews[0].intrinsic_size

  def layout_subviews(self):
    for sv in self.subviews:
      sv.frame = self.frame

  @property
  def can_unbecome_first_responder(self):
    return False

  @property
  def should_become_first_responder_immediately(self):
    return True

  def add_subviews(self, subviews):
    super().add_subviews(subviews)
    for v in subviews:
      for sv in v.postorder_traversal:
        if sv.should_become_first_responder_immediately:
          self.set_first_responder(sv)
          return

  def remove_subviews(self, subviews):
    super().remove_subviews(subviews)
    for v in subviews:
      for sv in v.postorder_traversal:
        if sv == self.first_responder:
          self.set_first_responder(None)
          self.find_next_responder()
          return

  def set_first_responder(self, new_value):
    if self.first_responder:
      self.first_responder.unbecome_first_responder()
    self.first_responder = new_value
    if self.first_responder:
      self.first_responder.become_first_responder()

  def find_next_responder(self):
    existing_responder = self.first_responder or self.leftmost_leaf
    all_responders = [v for v in self.postorder_traversal if v.can_become_first_responder]
    try:
      i = all_responders.index(existing_responder)
      if i == len(all_responders) - 1:
        self.set_first_responder(all_responders[0])
      else:
        self.set_first_responder(all_responders[i + 1])
    except ValueError:
      if all_responders:
        self.set_first_responder(all_responders[0])
      else:
        self.set_first_responder(None)

  def find_prev_responder(self):
    existing_responder = self.first_responder or self.leftmost_leaf
    all_responders = [v for v in self.postorder_traversal if v.can_become_first_responder]
    try:
      i = all_responders.index(existing_responder)
      if i == 0:
        self.set_first_responder(all_responders[-1])
      else:
        self.set_first_responder(all_responders[i - 1])
    except ValueError:
      if all_responders:
        self.set_first_responder(all_responders[-1])
      else:
        self.set_first_responder(None)

  def terminal_read(self, val):
    can_tab_away = (
      not self.first_responder
      or self.first_responder.can_unbecome_first_responder)
    if val == terminal.TK_TAB and can_tab_away:
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
    self.size = size or Size(0, 0)

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
      x = 0
      if self.behavior_x in ('begin', 'fill', 'constant'):
        x = self.frame.origin.x + self.inset.width
      elif self.behavior_x == 'middle':
        x = self.frame.center.x - view.intrinsic_size.width / 2
      elif self.behavior_x == 'end':
        x = (
          self.frame.origin.x +
          self.frame.size.width -
          view.intrinsic_size.width -
          self.inset.width)

      y = 0
      if self.behavior_y in ('begin', 'fill', 'constant'):
        y = self.frame.origin.y + self.inset.height
      elif self.behavior_y == 'middle':
        y = self.frame.center.y - view.intrinsic_size.height / 2
      elif self.behavior_y == 'end':
        y = (
          self.frame.origin.y +
          self.frame.size.height -
          view.intrinsic_size.height -
          self.inset.height)

      width = view.bounds.size.width
      if self.behavior_x == 'fill':
        width = self.frame.size.width - self.inset.width * 2
      elif self.behavior_x == 'constant':
        width = self.size.width - self.inset.width * 2

      height = view.bounds.size.height
      if self.behavior_y == 'fill':
        height = self.frame.size.height - self.inset.height * 2
      elif self.behavior_y == 'constant':
        height = self.size.height - self.inset.height * 2

      view.frame = Rect(Point(x, y), Size(width, height)).floored


class RectView(View):
  def __init__(self, color_fg='#aaaaaa', color_bg='#000000', *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.color_fg = color_fg
    self.color_bg = color_bg

  def draw(self):
    with temporary_color(self.color_fg, self.color_bg):
      for point in self.frame.points:
        terminal.put(point.x, point.y, ' ')
      for point in self.frame.points_top:
        terminal.put(point.x, point.y, '-')
      for point in self.frame.points_bottom:
        terminal.put(point.x, point.y, '-')
      for point in self.frame.points_left:
        terminal.put(point.x, point.y, '|')
      for point in self.frame.points_right:
        terminal.put(point.x, point.y, '|')
      for point in self.frame.points_corners:
        terminal.put(point.x, point.y, '+')
    super().draw()


class WindowView(RectView):
  def __init__(self, title=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.title_view = FillerView(
        behavior_x='center', behavior_y='constant', size=Size(0, 1),
        subviews=[
          LabelView(title),
        ])
    
    self.add_subviews([self.title_view])

  def layout_subviews(self):
    super().layout_subviews()
    for sv in self.subviews:
      if sv == self.title_view:
        sv.frame = self.frame.with_size(Size(self.frame.size.width, 1))
      else:
        sv.frame = self.frame


class CenteringView(View):
  def layout_subviews(self):
    center = self.frame.center
    for view in self.subviews:
      view.frame = view.bounds.with_origin(center - view.intrinsic_size / 2).floored


class FigletView(View):
  def __init__(self, font, text, color_fg='#ffffff', color_bg=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
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
    super().layout_subviews()
    self.label_view.frame = self.frame

  @property
  def can_become_first_responder(self):
    return True

  def terminal_read(self, val):
    if val == terminal.TK_ENTER:
      self.callback()