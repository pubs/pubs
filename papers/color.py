"""
Small code to handle colored text
"""
import re

bold = '\033[1m'
end  = '\033[0m'

black  = '\033[0;30m'
red    = '\033[0;31m'
green  = '\033[0;32m'
yellow = '\033[0;33m'
blue   = '\033[0;34m'
purple = '\033[0;35m'
cyan   = '\033[0;36m'
grey   = '\033[0;37m'

ok       = green
error    = red
normal   = grey
citekey  = purple
filepath = cyan

def dye(s, color=end, bold=False):
    assert color[0] == '\033'
    if bold:
        color = '\033[1' + color[3:]
    return color + s + end

_dye = dye
def _nodye(s, **kwargs):
    return s

def setup(enable = True):
    global dye
    if enable:
        dye = _dye
    else:
        dye = _nodye


undye_re = re.compile('\x1b\[[;\d]*[A-Za-z]')

def undye(s):
    """Purge string s of color"""
    return undye_re.sub('', s)