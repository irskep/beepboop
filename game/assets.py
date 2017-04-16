import json
from pathlib import Path

from appdirs import user_data_dir
from pyfiglet import Figlet


PATH_ASSETS = Path(__file__).parent.parent / 'assets'
PATH_GFX = PATH_ASSETS / 'gfx'
PATH_FONTS = PATH_ASSETS / 'fonts'
PATH_USER_DATA = Path(user_data_dir('com.steveasleep.beepboop'))
PATH_USER_DATA.mkdir(parents=True, exist_ok=True)
print(PATH_USER_DATA)
PATH_GAME_CONFIG = PATH_USER_DATA / 'settings.json'

FONT_LOGO = Figlet(font=str(PATH_ASSETS / 'figlet_fonts' / 'CalvinS.flf'))


def get_font_configs(size=16):
    return ""
    font_name_re_1 = re.compile(r'NotoSans(.*)-Regular.ttf')
    font_name_re_2 = re.compile(r'Noto(.*)-Regular.ttf')
    lines = []
    for file_path in PATH_FONTS.iterdir():
        m1 = font_name_re_1.match(file_path.name)
        m2 = font_name_re_1.match(file_path.name)
        if m1:
            lines.append('{} font: {}, size={};'.format(
                m1.groups(1)[0].lower(), str(file_path), size))
    return '\n'.join(lines)


def get_blt_config():
    return """
window.title='Beep Boop RL';
log.level=trace;
window.resizeable=true;
window.cellsize={cellsize};
font: assets/fonts/NotoMono-Regular.ttf, size={fontsize};
{fonts}""".format(fonts=get_font_configs(), **get_game_config())[1:]

def get_game_config():
    if PATH_GAME_CONFIG.exists():
        with PATH_GAME_CONFIG.open() as f:
            return json.load(f)
    else:
        return {
            'cellsize': '16x24',
            'fontsize': '12',
        }


def update_game_config(new_values):
    config = get_game_config()
    with PATH_GAME_CONFIG.open('w') as f:
        config.update(new_values)
        return json.dump(config, f)

print(get_game_config())