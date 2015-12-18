"""
Small code to handle colored text
"""
import sys
import re
import os

def _color_supported(stream):
    """Return True is the stream supports colors"""
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

def generate_colors(stream, color=True, bold=True, italic=True, force_colors=False):
    """Generate colors, based on configuration and detected support

    :param color:         generate colors. If False, bold and italic will not change
                          the current color.
    :param bold:          generate bold colors, if False, bold color are the same as
                          normal colors.
    :param italic:        generate italic colors
    :param force_colors:  generate colors whether support is detected or not. Will not
                          overrride the `color` parameter.
    """
    colors =            {name: u'' for name in COLOR_LIST}
    colors.update({u'b' +name: u'' for name in COLOR_LIST})
    colors.update({u'i' +name: u'' for name in COLOR_LIST})
    colors.update({u'bi'+name: u'' for name in COLOR_LIST})
    colors[u'bold']   = u''
    colors[u'italic'] = u''
    colors[u'end']    = u''
    colors[u'']       = u''

    color_support = force_colors or _color_supported(stream)

    if (color or bold or italic) and color_support:
        bold_flag, italic_flag = '', ''
        if bold:
            colors['bold'] = u'\033[1m'
            bold_flag = '1;'
        if italic:
            colors['italic'] = u'\033[3m'
            italic_flag = '3;'
        if bold and italic:
            colors['bolditalic'] = u'\033[1;3m'

        for i, name in enumerate(COLOR_LIST):
            if color:
                colors[name] = u'\x1b[3{}m'.format(i)
                colors.update({u'b'+name: u'\033[{}3{}m'.format(bold_flag, i) for i, name in enumerate(COLOR_LIST)})
                colors.update({u'i'+name: u'\033[{}3{}m'.format(italic_flag, i) for i, name in enumerate(COLOR_LIST)})
                colors.update({u'bi'+name: u'\033[{}{}3{}m'.format(bold_flag, italic_flag, i) for i, name in enumerate(COLOR_LIST)})
            else:
                if bold:
                    colors.update({u'b'+name: u'\033[1m' for i, name in enumerate(COLOR_LIST)})
                if italic:
                    colors.update({u'i'+name: u'\033[3m' for i, name in enumerate(COLOR_LIST)})
                if bold or italic:
                    colors.update({u'bi'+name: u'\033[{}{}m'.format(bold_flag, italic_flag) for i, name in enumerate(COLOR_LIST)})

        if color or bold or italic:
            colors['end'] = u'\033[0m'

    return colors


COLORS_OUT = generate_colors(sys.stdout, color=False, bold=False, italic=False)
COLORS_ERR = generate_colors(sys.stderr, color=False, bold=False, italic=False)


def dye_out(s, color='end'):
    """Color a string for output on stdout"""
    return u'{}{}{}'.format(COLORS_OUT[color], s, COLORS_OUT['end'])

def dye_err(s, color='end'):
    """Color a string for output on stderr"""
    return u'{}{}{}'.format(COLORS_ERR[color], s, COLORS_OUT['end'])


def setup(conf, force_colors=False):
    """Prepare color for stdout and stderr"""
    global COLORS_OUT, COLORS_ERR
    COLORS_OUT = generate_colors(sys.stdout, force_colors=force_colors,
                                 color=conf['formating']['color'],
                                 bold=conf['formating']['bold'],
                                 italic=conf['formating']['italics'])
    COLORS_ERR = generate_colors(sys.stderr, force_colors=force_colors,
                                 color=conf['formating']['color'],
                                 bold=conf['formating']['bold'],
                                 italic=conf['formating']['italics'])
    for key, value in conf['theme'].items():
        COLORS_OUT[key] = COLORS_OUT.get(value, '')
        COLORS_ERR[key] = COLORS_ERR.get(value, '')


# undye
undye_re = re.compile('\x1b\[[;\d]*[A-Za-z]')

def undye(s):
    """Purge string s of color"""
    return undye_re.sub('', s)
