from pathlib import Path

from pyfiglet import Figlet


PATH_ASSETS = Path(__file__).parent.parent / 'assets'
PATH_GFX = PATH_ASSETS / 'gfx'

FONT_LOGO = Figlet(font=str(PATH_ASSETS / 'figlet_fonts' / 'CalvinS.flf'))


def get_logo():
    return FONT_LOGO.renderText('BeepBoop')
    with (PATH_GFX / 'logo.txt').open('r') as f:
        return f.read()