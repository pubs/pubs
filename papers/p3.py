import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    import StringIO as io
    input = raw_input
else:
    import configparser
    import io

configparser = configparser
io = io
input = input