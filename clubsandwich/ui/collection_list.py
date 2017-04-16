from .view import View
from .misc_views import LabelView, RectView
from ..geom import Rect, Point, Size


class ListView(RectView):
  def __init__(self, label_control_pairs, value_column_width=16, *args, **kwargs):
    super().__init__(subviews=[], *args, **kwargs)
    self.min_row = 0
    self.value_column_width = value_column_width

    self.labels = [LabelView(t) for t, _ in label_control_pairs]
    self.values = [c for _, c in label_control_pairs]
    self.add_subviews(self.labels)
    self.add_subviews(self.values)

  def get_is_in_view(self, y):
    return (
      y >= self.min_row and
      y <= self.min_row + self.inner_height)

  @property
  def inner_height(self):
    return self.frame.height - 3

  def scroll_to(self, y):
    if not self.frame.height:
      return  # metrics are garbage right now

    if y < self.min_row:
      self.min_row = y
    elif y > self.min_row + self.inner_height:
      self.min_row = max(0, min(y - self.inner_height, len(self.labels) - self.inner_height))
    self.set_needs_layout()

  def layout_subviews(self):
    for i in range(len(self.labels)):
      is_in_view = self.get_is_in_view(i)
      if is_in_view:
        y = 1 + self.frame.y + i - self.min_row
        self.labels[i].frame = Rect(
          Point(self.frame.x + 1, y),
          Size(self.frame.width - self.value_column_width - 2, 1))
        self.values[i].frame = Rect(
          Point(self.frame.x + 1 + self.frame.width - self.value_column_width - 2, y),
          Size(self.value_column_width, 1))
      self.labels[i].is_hidden = not is_in_view
      self.values[i].is_hidden = not is_in_view

  def descendant_did_become_first_responder(self, control):
    for i in range(len(self.labels)):
      if self.values[i] == control:
        if not self.get_is_in_view(i):
          self.scroll_to(i)
        break
    