# display

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

def colored(s, color=end, bold=False):
    if bold:
        s = '\033[1' + s[3:]
    return color + s + end
