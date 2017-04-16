#!/usr/bin/env python
from math import floor

from bearlibterminal import terminal
from clubsandwich.blt_state import blt_state
from clubsandwich.director import DirectorLoop, Scene
from clubsandwich.geom import Rect, Point, Size
from clubsandwich.ui import (
    FillerView,
    FigletView,
    VerticalSplitView,
    HorizontalSplitView,
    LabelView,
    ButtonView,
    FirstResponderContainerView,
    WindowView,
    ListView,
)
from game.assets import (
    get_blt_config,
    FONT_LOGO,
    get_game_config,
    update_game_config,
)


class UIScene(Scene):
    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.view = FirstResponderContainerView(subviews=[view], scene=self)
        self.add_terminal_reader(self.view)

    def terminal_read(self, val):
        super().terminal_read(val)
        if val == terminal.TK_BACKSLASH:
            self.view.debug_print()

    def terminal_update(self, is_active=False):
        self.view.frame = self.view.frame.with_size(
            Size(blt_state.width, blt_state.height))
        self.view.perform_layout()
        self.view.perform_draw()


class MainMenuScene(UIScene):
    def __init__(self, *args, **kwargs):
        view = VerticalSplitView(subviews=[
            FillerView(subviews=[
                FigletView(FONT_LOGO, 'BeepBoop')
            ]),
            HorizontalSplitView(subviews=[
                FillerView(),
                FillerView(subviews=[ButtonView(
                    text="Settings", callback=self.show_settings)]),
                FillerView(subviews=[ButtonView(
                    text="Play", callback=self.play)]),
                FillerView(subviews=[ButtonView(
                    text="Exit", callback=lambda: self.director().pop_scene())]),
                FillerView(),
            ])
        ])
        super().__init__(view, *args, **kwargs)

    def play(self):
        self.director().push_scene(CharacterCreationScene())

    def show_settings(self):
        self.director().push_scene(SettingsScene())


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


class SettingsScene(UIScene):
    TILE_SIZES = ['16x24', '24x36', '32x48']
    FONT_SIZES = ['12', '18', '24']

    def __init__(self, *args, **kwargs):
        self.tile_size = get_game_config()['cellsize']
        self.font_size = get_game_config()['fontsize']

        self.button_tile_size = ButtonView(
            text=self.tile_size,
            callback=self.rotate_tile_size)

        view = FillerView(
            behavior_x='center', behavior_y='center',
            size=Size(50, 20),
            subviews=[
                WindowView('Settings', subviews=[
                    VerticalSplitView(ratios=[0.75, 0.25], subviews=[
                        ListView([
                            ('Tile size', self.button_tile_size),
                        ]),
                        HorizontalSplitView(subviews=[
                            FillerView(subviews=[
                                ButtonView(
                                    text='Apply', callback=self.apply),
                            ]),
                            FillerView(subviews=[
                                ButtonView(
                                    text='Cancel', callback=lambda: self.director().pop_scene()),
                            ]),
                        ]),
                    ]),
                ])
            ])
        super().__init__(view, *args, **kwargs)

    def rotate_tile_size(self):
        sizes = SettingsScene.TILE_SIZES
        for i, s in enumerate(sizes):
            if s == self.tile_size:
                j = (i + 1) % len(sizes)
                self.tile_size = sizes[j]
                self.font_size = SettingsScene.FONT_SIZES[j]
                self.button_tile_size.text = self.tile_size
                break

    def apply(self):
        update_game_config({
            'cellsize': self.tile_size,
            'fontsize': self.font_size,
        })
        self.director().pop_scene()


class TestLoop(DirectorLoop):
    def terminal_init(self):
        super().terminal_init()

        config = get_blt_config()
        print("CONFIG:")
        print(config)
        terminal.set(config)

    def get_initial_scene(self):
        return MainMenuScene()


if __name__ == '__main__':
    TestLoop().run()