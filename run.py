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
    ButtonView,
    FirstResponderContainerView,
)
from game.assets import get_config, FONT_LOGO


class UIScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.should_exit = False

        self.view = FirstResponderContainerView(subviews=[
            VerticalSplitView(subviews=[
                CenteringView(subviews=[
                    FigletView(FONT_LOGO, 'BeepBoop')
                ]),
                HorizontalSplitView(subviews=[
                    CenteringView(),
                    CenteringView(subviews=[ButtonView(
                        text="Play", callback=lambda: print("play!"))]),
                    CenteringView(subviews=[ButtonView(
                        text="Settings", callback=lambda: print("settings!"))]),
                    CenteringView(subviews=[ButtonView(
                        text="Exit", callback=self.exit)]),
                    CenteringView(),
                ])
            ])
        ])
        self.add_terminal_reader(self.view)

    def exit(self):
        self.should_exit = True

    def terminal_update(self):
        self.view.frame = self.view.frame.with_size(
            Size(blt_state.width, blt_state.height))
        self.view.perform_layout()
        self.view.draw()
        return not self.should_exit


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