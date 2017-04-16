from math import floor

from ..blt_nice_terminal import terminal
from ..blt_state import blt_state
from .view import View


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
      for ancestor in self.first_responder.ancestors:
        ancestor.descendant_did_unbecome_first_responder(self.first_responder)
    self.first_responder = new_value
    if self.first_responder:
      self.first_responder.become_first_responder()
      for ancestor in self.first_responder.ancestors:
        ancestor.descendant_did_become_first_responder(self.first_responder)

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