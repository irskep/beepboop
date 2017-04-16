#!/usr/bin/env python
from math import floor

from bearlibterminal import terminal
from clubsandwich.blt_state import blt_state
from clubsandwich.director import DirectorLoop, Scene
from clubsandwich.geom import Rect, Point, Size
from clubsandwich.ui import (
    CenteringView,
    FillerView,
    FigletView,
    VerticalSplitView,
    HorizontalSplitView,
    LabelView,
    ButtonView,
    FirstResponderContainerView,
    WindowView,
)
from game.assets import get_config, FONT_LOGO


class UIScene(Scene):
    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.view = FirstResponderContainerView(subviews=[view])
        self.add_terminal_reader(self.view)

    def terminal_update(self, is_active=False):
        self.view.frame = self.view.frame.with_size(
            Size(blt_state.width, blt_state.height))
        self.view.perform_layout()
        self.view.draw()


class MainScreenScene(UIScene):
    def __init__(self, *args, **kwargs):
        view = VerticalSplitView(subviews=[
            CenteringView(subviews=[
                FigletView(FONT_LOGO, 'BeepBoop')
            ]),
            HorizontalSplitView(subviews=[
                CenteringView(),
                CenteringView(subviews=[ButtonView(
                    text="Play", callback=self.play)]),
                CenteringView(subviews=[ButtonView(
                    text="Settings", callback=lambda: view.debug_print())]),
                CenteringView(subviews=[ButtonView(
                    text="Exit", callback=lambda: self.director().pop_scene())]),
                CenteringView(),
            ])
        ])
        super().__init__(view, *args, **kwargs)

    def play(self):
        self.director().push_scene(CharacterCreationScene())


class CharacterCreationScene(UIScene):
    def __init__(self, *args, **kwargs):
        view = FillerView(
            behavior_x='fill', behavior_y='fill',
            inset=Size(10, 7),
            subviews=[
                WindowView('Character', subviews=[
                    HorizontalSplitView(subviews=[
                        FillerView(subviews=[
                            ButtonView(
                                text='Debug', callback=lambda: view.debug_print()),
                        ]),
                        FillerView(subviews=[
                            ButtonView(
                                text='Cancel', callback=lambda: self.director().pop_scene()),
                        ]),
                    ]),
                ])
            ])
        super().__init__(view, *args, **kwargs)

    def play(self):
        self.director().push_scene(CharacterCreationScene())


class TestLoop(DirectorLoop):
    def get_initial_scene(self):
        return MainScreenScene()

    def terminal_init(self):
        super().terminal_init()

        config = get_config()
        print("CONFIG:")
        print(config)
        terminal.set(config)


if __name__ == '__main__':
    TestLoop().run()