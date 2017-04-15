#!/usr/bin/env python
import asyncio
import re
from math import floor
from pathlib import Path

from bearlibterminal import terminal
from clubsandwich.blt_loop import BearLibTerminalEventLoop
from clubsandwich.blt_state import blt_state
from game.assets import get_logo


def get_font_configs(dir_path, size=16):
    return ""
    font_name_re_1 = re.compile(r'NotoSans(.*)-Regular.ttf')
    font_name_re_2 = re.compile(r'Noto(.*)-Regular.ttf')
    lines = []
    for file_path in dir_path.iterdir():
        m1 = font_name_re_1.match(file_path.name)
        m2 = font_name_re_1.match(file_path.name)
        if m1:
            lines.append('{} font: {}, size={};'.format(
                m1.groups(1)[0].lower(), str(file_path), size))
    return '\n'.join(lines)


class TestLoop(BearLibTerminalEventLoop):
    def terminal_init(self):
        """
        The superclass has already configured BearLibTerminal at this point.

        See blt_loop.py for details.
        """

        print("CONFIG:")
        config = """
window.title='Beep Boop RL';
log.level=trace;
font: fonts/NotoMono-Regular.ttf, size=16;
{}""".format(get_font_configs(Path(__file__).parent / 'fonts'))
        print(config[1:])

        terminal.set(config)

    def terminal_update(self):
        logo_str = get_logo()
        logo_width = max(len(s) for s in logo_str.split('\n'))
        logo_height = sum(1 for c in logo_str if c == '\n')
        x = floor(blt_state.width / 2 - logo_width / 2)
        y = floor(blt_state.height / 4 - logo_height / 2)
        terminal.print(x, y, get_logo())
        #terminal.printf(2, 1, "[font=mono]Hello, [color=white]world! [font=brahmi]" + chr(69636))
        return True


if __name__ == '__main__':
    TestLoop().run()