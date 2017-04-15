#!/usr/bin/env python
from math import floor

from bearlibterminal import terminal
from clubsandwich.blt_state import blt_state
from clubsandwich.director import DirectorLoop, Scene
from clubsandwich.geom import Rect, Point, Size
from clubsandwich.ui import CenteringView, FigletView
from game.assets import get_config, FONT_LOGO


class UIScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = CenteringView(Rect(Point(0, 0), Size(0, 0)), [
            FigletView(FONT_LOGO, 'BeepBoop')
        ])

    def terminal_update(self):
        self.view.frame = self.view.frame.with_size(
            Size(blt_state.width, blt_state.height))
        self.view.perform_layout()
        self.view.draw()
        return True


class TestLoop(DirectorLoop):
    def get_initial_scene(self):
        return UIScene()

    def terminal_init(self):
        super().terminal_init()

        config = get_config()
        print("CONFIG:")
        print(config)
        terminal.set(config)


if __name__ == '__main__':
    TestLoop().run()