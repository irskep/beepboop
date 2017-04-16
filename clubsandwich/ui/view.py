import weakref
from ..geom import Point, Rect, Size


class View:
  def __init__(self, frame=None, subviews=None, scene=None):
    self._scene = scene
    self._superview_weakref = lambda: None
    self.needs_layout = True
    self._frame = frame or Rect(Point(0, 0), Size(0, 0))
    self._bounds = self.frame.with_origin(Point(0, 0))
    self.subviews = []
    self.add_subviews(subviews or [])
    self.is_first_responder = False
    self.is_hidden = False

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

  def perform_draw(self):
    if self.is_hidden:
      return
    self.draw()
    for view in self.subviews:
      view.perform_draw()

  def draw(self):
    pass

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