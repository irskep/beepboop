import weakref
from collections import namedtuple
from numbers import Real

from clubsandwich.geom import Point, Rect, Size
from clubsandwich.blt.context import BearLibTerminalContext
from .layout_options import LayoutOptions


ZERO_RECT = Rect(Point(0, 0), Size(0, 0)) 


class View:
  def __init__(self, frame=None, subviews=None, scene=None, layout_options=None):
    if isinstance(layout_options, dict):  # have pity on the user's imports
      opts = LayoutOptions()._asdict()
      opts.update(layout_options)
      layout_options = LayoutOptions(**opts)
    self._scene = scene
    self._superview_weakref = lambda: None
    self.needs_layout = True
    self._frame = frame or ZERO_RECT
    self._bounds = self.frame.with_origin(Point(0, 0))
    self.subviews = []
    self.add_subviews(subviews or [])
    self.is_first_responder = False
    self.is_hidden = False

    self.layout_spec = frame
    self.layout_options = layout_options or LayoutOptions()

  ### core api ###

  @property
  def scene(self):
    if self._scene:
      return self._scene
    else:
      return self.superview.scene

  @property
  def superview(self):
    return self._superview_weakref()

  @superview.setter
  def superview(self, new_value):
    if new_value:
      self._superview_weakref = weakref.ref(new_value)
    else:
      self._superview_weakref = lambda: None

  def set_needs_layout(self, val=True):
    self.needs_layout = val

  def add_subviews(self, subviews):
    for v in subviews:
      v.superview = self
    self.subviews.extend(subviews)

  def remove_subviews(self, subviews):
    for v in subviews:
      v.superview = None
    self.subviews = [v for v in self.subviews if v not in subviews]

  def perform_draw(self, ctx=None):
    ctx = ctx or BearLibTerminalContext()
    if self.is_hidden:
      return
    self.draw(ctx)
    for view in self.subviews:
      with ctx.translate(view.frame.origin):
        view.perform_draw(ctx)

  def draw(self, ctx):
    pass

  def perform_layout(self):
    if self.needs_layout:
      self.layout_subviews()
      self.needs_layout = False
    for view in self.subviews:
      view.perform_layout()

  def layout_subviews(self):
    """
    Set the frames of all subviews relative to ``self.bounds``. By default,
    applies the springs-and-struts algorithm using each view's
    ``layout_options`` and ``layout_spec`` properties.
    """
    for view in self.subviews:
      _apply_springs_and_struts_layout_to_view(view)

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
  def can_did_become_first_responder(self):
    return False

  @property
  def can_did_resign_first_responder(self):
    return True

  def did_become_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = True

  def did_resign_first_responder(self):
    self.set_needs_layout(True)
    self.is_first_responder = False

  def descendant_did_become_first_responder(self, view):
    """
    Called by FirstResponderContainerView when any descendant of this view
    becomes the first responder. This is so list implementations can scroll it
    into view.
    """
    pass

  def descendant_did_resign_first_responder(self, view):
    """
    Called by FirstResponderContainerView when any descendant of this view
    unbecomes the first responder. This is so list implementations can release
    keyboard event handlers.
    """
    pass

  def terminal_read(self, val):
    """
    Fires when an input event occurs, and either:
    * This view is the first responder
    * The first responder is a descendant, and no other descendants have
      already handled this event

    You must return a truthy value if you handled the event so it doesn't get
    handled twice.
    """
    return False

  @property
  def first_responder_container_view(self):
    if hasattr(self, 'first_responder'):
      return self
    for v in self.ancestors:
      if hasattr(v, 'first_responder'):
        return v
    return None

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
  def ancestors(self):
    v = self.superview
    while v:
      yield v
      v = v.superview

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


def _option_field_to_id(val):
    if val == 'frame':
      value_start = 'frame'
    elif isinstance(val, Real):
      value_start = 'fraction'
    else:
      value_start = 'derive'


def _apply_springs_and_struts_layout_to_view(view):
  options = view.layout_options
  spec = view.layout_spec
  superview_bounds = view.superview.bounds

  fields = [
    ('left', 'right', 'x', 'width'),
    ('top', 'bottom', 'y', 'height'),
  ]

  final_frame = Rect(Point(-1000, -1000), Size(-1000, -1000))

  for field_start, field_end, field_coord, field_size in fields:
    debug_string = options.get_debug_string_for_keys(
        [field_start, field_size, field_end])
    matches = (
      options.get_is_defined(field_start),
      options.get_is_defined(field_size),
      options.get_is_defined(field_end))
    if matches == (True, True, True):
      raise ValueError("Invalid spring/strut definition: {}".format(debug_string))
    if matches == (False, False, False):
      raise ValueError("Invalid spring/strut definition: {}".format(debug_string))
    elif matches == (True, False, False):
      setattr(
        final_frame, field_coord,
        options.get_value(field_start, view))
      # pretend that size is constant from frame
      setattr(
        final_frame, field_size,
        getattr(spec, field_size))
    elif matches == (True, True, False):
      setattr(
        final_frame, field_coord,
        options.get_value(field_start, view))
      setattr(
        final_frame, field_size,
        options.get_value(field_size, view))
    elif matches == (False, True, False):  # magical centering!
      size_val = options.get_value(field_size, view)
      setattr(final_frame, field_size, size_val)
      setattr(
        final_frame, field_coord,
        getattr(superview_bounds, field_size) / 2 - size_val / 2)
    elif matches == (False, True, True):
      size_val = options.get_value(field_size, view)
      setattr(
        final_frame, field_coord,
        getattr(superview_bounds, field_size) - options.get_value(field_end, view) - size_val)
      setattr(final_frame, field_size, size_val)
    elif matches == (False, False, True):
      setattr(
        final_frame, field_coord,
        getattr(superview_bounds, field_size) - options.get_value(field_end, view))
      # pretend that size is constant from frame
      setattr(final_frame, field_size, getattr(spec, field_size))
    elif matches == (True, False, True):
      start_val = options.get_value(field_start, view) 
      end_val = options.get_value(field_end, view) 
      setattr(
        final_frame, field_coord, start_val)
      setattr(
        final_frame, field_size,
        getattr(superview_bounds, field_size) - start_val - end_val)
    else:
      raise ValueError("Unhandled case: {}".format(debug_string))

  assert(final_frame.x != -1000)
  assert(final_frame.y != -1000)
  assert(final_frame.width != -1000)
  assert(final_frame.height != -1000)
  view.frame = final_frame.floored
