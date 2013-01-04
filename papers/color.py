# display

BOLD = '\033[1m'
END  = '\033[0m'

COLORS = {
    'black' : '\033[0;30m',
    'red'   : '\033[0;31m',
    'green' : '\033[0;32m',
    'yellow': '\033[0;33m',
    'blue'  : '\033[0;34m',
    'purple': '\033[0;35m',
    'cyan'  : '\033[0;36m',
    'grey'  : '\032[0;37m',
    }

# Bold
BCOLORS = {
    'black' : '\033[1;30m',
    'red'   : '\033[1;31m',
    'green' : '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue'  : '\033[1;34m',
    'purple': '\033[1;35m',
    'cyan'  : '\033[1;36m',
    'grey'  : '\033[1;37m',
    }

# application specific
ALIASES = {
    'ok'      : 'green',
    'error'   : 'red',
    'normal'  : 'grey',
    'citekey' : 'purple',
    'filepath': 'cyan',
    }


def colored(s, color=None, bold=False):
    if color in ALIASES:
        color = ALIASES[color]
    try:
        if bold:
            color_code = BCOLORS[color]
        else:
            color_code = COLORS[color]
    except KeyError:
        if bold:
            color_code = CODE
        else:
            color_code = ''
    if color_code != '':
        end_code = END
    else:
        end_code = ''
    return color_code + s + end_code
