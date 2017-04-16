#!/usr/bin/env python
from math import floor

from bearlibterminal import terminal
from clubsandwich.blt_state import blt_state
from clubsandwich.director import DirectorLoop, Scene
from clubsandwich.geom import Rect, Point, Size
from clubsandwich.ui import (
    LabelView,
    ButtonView,
    FirstResponderContainerView,
    WindowView,
    ListView,
    LayoutOptions,
)
from game.assets import (
    get_blt_config,
    FONT_LOGO,
    get_game_config,
    update_game_config,
    get_image,
)


class UIScene(Scene):
    def __init__(self, views, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(views, list):
            views = [views]

        self.view = FirstResponderContainerView(subviews=views, scene=self)
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
        views = [
            LabelView(
                FONT_LOGO.renderText('BeepBoop'),
                layout_options=LayoutOptions.row_top(0.3)),
            LabelView(
                get_image('robot'),
                layout_options=LayoutOptions(top=0.3, bottom=4)),
            ButtonView(
                text="Play", callback=self.play,
                layout_options=LayoutOptions.row_bottom(4).with_updates(left=0.2, width=0.2, right=None)),
            ButtonView(
                text="Settings", callback=self.show_settings,
                layout_options=LayoutOptions.row_bottom(4).with_updates(left=0.4, width=0.2, right=None)),
            ButtonView(
                text="Quit", callback=lambda: self.director().pop_scene(),
                layout_options=LayoutOptions.row_bottom(4).with_updates(left=0.6, width=0.2, right=None)),
        ]
        super().__init__(views, *args, **kwargs)

    def play(self):
        self.director().push_scene(CharacterCreationScene())

    def show_settings(self):
        self.director().push_scene(SettingsScene())


class CharacterCreationScene(UIScene):
    def __init__(self, *args, **kwargs):
        view = WindowView(
            'Character',
            layout_options=LayoutOptions(top=7, right=10, bottom=7, left=10),
            subviews=[
                LabelView('There is no game yet.', layout_options=LayoutOptions.row_top(0.5)),
                ButtonView(
                    text='Darn', callback=lambda: self.director().pop_scene(),
                    layout_options=LayoutOptions.row_bottom(0.5)),
            ]
        )
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

        view = WindowView(
            'Settings',
            layout_options=LayoutOptions.centered(50, 20),
            subviews=[
            ListView(
                [
                    ('Tile size', self.button_tile_size),
                ] + [
                    ('Filler ' + str(i), ButtonView(text='Hi', callback=lambda: None))
                    for i in range(50)
                ],
                layout_options=LayoutOptions(bottom=3)),
            ButtonView(
                text='Apply', callback=self.apply,
                layout_options=LayoutOptions.row_bottom(3).with_updates(right=0.5)),
            ButtonView(
                text='Cancel', callback=lambda: self.director().pop_scene(),
                layout_options=LayoutOptions.row_bottom(3).with_updates(left=0.5)),
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