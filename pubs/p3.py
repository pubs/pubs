import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    import StringIO as io
    input = raw_input
    ustr = unicode
else:
    import configparser
    import io
    ustr = str

configparser = configparser
io = io
input = input
