#!/usr/bin/env python
from math import floor

from bearlibterminal import terminal
from clubsandwich.blt_state import blt_state
from clubsandwich.director import DirectorLoop, Scene
from clubsandwich.geom import Rect, Point, Size
from clubsandwich.ui import (
    CenteringView,
    FigletView,
    VerticalSplitView,
    HorizontalSplitView,
    LabelView,
)
from game.assets import get_config, FONT_LOGO


class UIScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = VerticalSplitView(subviews=[
            CenteringView(subviews=[
                FigletView(FONT_LOGO, 'BeepBoop')
            ]),
            HorizontalSplitView(subviews=[
                CenteringView(),
                CenteringView(subviews=[LabelView(text="Play")]),
                CenteringView(subviews=[LabelView(text="Settings")]),
                CenteringView(subviews=[LabelView(text="Exit")]),
                CenteringView(),
            ])
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