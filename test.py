#!/usr/bin/env python
import asyncio
import re
from pathlib import Path

from bearlibterminal import terminal
from blt_loop import BearLibTerminalEventLoop


def get_font_configs(dir_path, size=16):
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
mono font: fonts/NotoMono-Regular.ttf, size=16;
{}""".format(get_font_configs(Path(__file__).parent / 'fonts'))
        print(config[1:])
        terminal.set(config)
        terminal.color('#ff0000')
        terminal.printf(2, 1, "[font=mono]Hello, [color=white]world! [font=brahmi]𑀄")

    def terminal_update(self):
        return True


if __name__ == '__main__':
    TestLoop().run()