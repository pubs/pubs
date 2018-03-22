"""
Code to handle colored text

Here is a little explanation about bash color code, useful to understand
the code below. See http://invisible-island.net/xterm/ctlseqs/ctlseqs.html
for a complete referece.

# 8 colors
The code `\033[{c}m` generate a color, with 30 <= c < 38. The order is:
'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'grey'.

Additionaly, adding `1;` and `3;` will generate bold and italic text,
respectively, so `\033[1;3;31m` would be bold italic red. Bold and italic
can also be used independently, so `\033[1m` would create bold text without
changing the current color.

Bold and italic will only be displayed if the terminal allows it *and* the
font supports it (thus, no italic with Monaco). Sometimes, bold is replaced
by the bright version of the font; some terminals allow the user to decide that.

# 256 colors
256 colors work the same. The code `\033[38;5;{c}` with 0 <= c < 256 will
display colors, with 0 <= c < 8 corresponding to the 8 above colors, and
8 <= c < 16 their bright version.
"""
from __future__ import unicode_literals

import sys
import re
import os
import subprocess


COLOR_LIST = {'black': '0', 'red': '1', 'green': '2', 'yellow': '3', 'blue': '4',
              'magenta': '5', 'cyan': '6', 'grey': '7',
              'brightblack': '8', 'brightred': '9', 'brightgreen': '10',
              'brightyellow': '11', 'brightblue': '12', 'brightmagenta': '13',
              'brightcyan': '14', 'brightgrey': '15',
              'darkgrey': '8', # == brightblack
              'gray': '7', 'darkgray': '8', 'brightgray': '15', # gray/grey spelling
              'purple': '5', # for compatibility reasons
              'white': '15' # == brightgrey
             }
for c in range(256):
    COLOR_LIST[str(c)] = str(c)


def _color_supported(stream, force=False):
    """Return the number of supported colors"""
    min_colors = 8 if force else 0
    if sys.platform == 'win32' and 'ANSICON' not in os.environ:
        return min_colors

    if hasattr(stream, 'isatty') and stream.isatty(): # we have a tty
        try:
            import curses
            curses.setupterm()
            return max(min_colors, curses.tigetnum('colors'))
        except Exception: # not picky.
            pass

    if force:
        p = subprocess.Popen(['tput', 'colors'], stdout=subprocess.PIPE)
        return max(min_colors, int(p.communicate()[0]))
    return 0

def generate_colors(stream, color=True, bold=True, italic=True, force_colors=False):
    """Generate 256 colors, based on configuration and detected support

    :param color:         generate colors. If False, bold and italic will not change
                          the current color.
    :param bold:          generate bold colors, if False, bold color are the same as
                          normal colors.
    :param italic:        generate italic colors
    """
    colors = {'bold': '', 'italic': '', 'end': '', '': ''}
    for name, code in COLOR_LIST.items():
        colors[name]      = ''
        colors['b' +name] = ''
        colors['i' +name] = ''
        colors['bi'+name] = ''

    color_support = _color_supported(stream, force=force_colors) >= 8

    if (color or bold or italic) and color_support:
        bold_flag, italic_flag = '', ''
        if bold:
            colors['bold'] = '\033[1m'
            bold_flag = '1;'
        if italic:
            colors['italic'] = '\033[3m'
            italic_flag = '3;'
        if bold and italic:
            colors['bolditalic'] = '\033[1;3m'

        for name, code in COLOR_LIST.items():
            if color:
                colors[name] = '\033[38;5;{}m'.format(code)
                colors['b'+name] = '\033[{}38;5;{}m'.format(bold_flag, code)
                colors['i'+name] = '\033[{}38;5;{}m'.format(italic_flag, code)
                colors['bi'+name] = '\033[{}38;5;{}m'.format(bold_flag, italic_flag, code)

            else:
                if bold:
                    colors.update({'b'+name: '\033[1m' for i, name in enumerate(COLOR_LIST)})
                if italic:
                    colors.update({'i'+name: '\033[3m' for i, name in enumerate(COLOR_LIST)})
                if bold or italic:
                    colors.update({'bi'+name: '\033[{}{}m'.format(bold_flag, italic_flag) for i, name in enumerate(COLOR_LIST)})

        if color or bold or italic:
            colors['end'] = '\033[0m'

    return colors


COLORS_OUT = generate_colors(sys.stdout, color=False, bold=False, italic=False)
COLORS_ERR = generate_colors(sys.stderr, color=False, bold=False, italic=False)


def dye_out(s, color='end'):
    """Color a string for output on stdout"""
    return '{}{}{}'.format(COLORS_OUT[color], s, COLORS_OUT['end'])

def dye_err(s, color='end'):
    """Color a string for output on stderr"""
    return '{}{}{}'.format(COLORS_ERR[color], s, COLORS_OUT['end'])


def setup(conf, force_colors=False):
    """Prepare color for stdout and stderr"""
    global COLORS_OUT, COLORS_ERR
    COLORS_OUT = generate_colors(sys.stdout, force_colors=force_colors,
                                 color =conf['formating']['color'],
                                 bold  =conf['formating']['bold'],
                                 italic=conf['formating']['italics'])
    COLORS_ERR = generate_colors(sys.stderr, force_colors=force_colors,
                                 color =conf['formating']['color'],
                                 bold  =conf['formating']['bold'],
                                 italic=conf['formating']['italics'])
    for key, value in conf['theme'].items():
        COLORS_OUT[key] = COLORS_OUT.get(value, '')
        COLORS_ERR[key] = COLORS_ERR.get(value, '')


# undye
undye_re = re.compile('\x1b\[[;\d]*[A-Za-z]')

def undye(s):
    """Purge string s of color"""
    return undye_re.sub('', s)
