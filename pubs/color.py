"""
Small code to handle colored text
"""
import sys
import re

def _color_supported(stream):
    """Returns True is the stream supports colors"""
    if sys.platform == 'win32' and 'ANSICON' not in os.environ:
        return False
    if hasattr(stream, 'isatty') and stream.isatty(): # we have a tty
        try:
            import curses
            curses.setupterm()
            return curses.tigetnum('colors') >= 8
        except Exception: # not picky.
            return False
    return False

COLOR_LIST = [u'black', u'red', u'green', u'yellow', u'blue', u'purple', u'cyan', u'grey']

def generate_colors(stream, color=True, bold=True, italic=True):
    colors =            {name: u'' for name in COLOR_LIST}
    colors.update({u'b' +name: u'' for name in COLOR_LIST})
    colors.update({u'i' +name: u'' for name in COLOR_LIST})
    colors.update({u'bi'+name: u'' for name in COLOR_LIST})
    colors[u'bold']   = u''
    colors[u'italic'] = u''
    colors[u'end']    = u''

    if (color or bold or italic) and _color_supported(stream):
        bold_flag, italic_flag = '', ''
        if bold:
            colors['bold'] = u'\x1b[1m'
            bold_flag = '1;'
        if italic:
            colors['italic'] = u'\x1b[3m'
            italic_flag = '3;'

        for i, name in enumerate(COLOR_LIST):
            if color:
                color_flag = '3{}'.format(name)
                colors[name] = u'\x1b[{}m'.format(color_flag)
                colors.update({u'b'+name: u'\x1b[{}3{}m'.format(bold_flag, i) for i, name in enumerate(COLOR_LIST)})
                colors.update({u'i'+name: u'\x1b[{}3{}m'.format(italic_flag, i) for i, name in enumerate(COLOR_LIST)})
                colors.update({u'bi'+name: u'\x1b[{}3{}m'.format(bold_flag, italic_flag, i) for i, name in enumerate(COLOR_LIST)})
            else:
                if bold:
                    colors.update({u'b'+name: u'\x1b[{}m'.format(bold_flag, i) for i, name in enumerate(COLOR_LIST)})
                if italic:
                    colors.update({u'i'+name: u'\x1b[{}m'.format(italic_flag, i) for i, name in enumerate(COLOR_LIST)})
                if bold or italic:
                    colors.update({u'bi'+name: u'\x1b[{}m'.format(bold_flag, italic_flag, i) for i, name in enumerate(COLOR_LIST)})

        if color or bold or italic:
            colors[u'end'] = u'\x1b[0m'

    return colors


COLORS_OUT = generate_colors(sys.stdout, color=True, bold=True, italic=True)
COLORS_ERR = generate_colors(sys.stderr, color=True, bold=True, italic=True)

def dye_out(s, color='end'):
    return '{}{}{}'.format(COLORS_OUT[color], s, COLORS_OUT['end'])

def dye_err(s, color='end'):
    return '{}{}{}'.format(COLORS_ERR[color], s, COLORS_OUT['end'])

def _nodye(s, *args, **kwargs):
    return s

def setup(color=True, bold=True, italic=True):
    global COLORS_OUT, COLORS_ERR
    COLORS_OUT = generate_colors(sys.stdout, color=color, bold=color, italic=color)
    COLORS_ERR = generate_colors(sys.stderr, color=color, bold=color, italic=color)

# undye
undye_re = re.compile('\x1b\[[;\d]*[A-Za-z]')

def undye(s):
    """Purge string s of color"""
    return undye_re.sub('', s)

# colors
ok       = 'green'
error    = 'red'
citekey  = 'purple'
filepath = 'bold'
tag      = 'cyan'
