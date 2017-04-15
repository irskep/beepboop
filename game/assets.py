from pathlib import Path

from pyfiglet import Figlet


PATH_ASSETS = Path(__file__).parent.parent / 'assets'
PATH_GFX = PATH_ASSETS / 'gfx'
PATH_FONTS = PATH_ASSETS / 'fonts'

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


def get_config():
    return """
window.title='Beep Boop RL';
log.level=trace;
window.resizeable=true;
font: assets/fonts/NotoMono-Regular.ttf, size=16;
{}""".format(get_font_configs())[1:]