import io
import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    _read_config = configparser.SafeConfigParser.readfp

    def input():
        raw_input().decode(sys.stdin.encoding or 'utf8', 'ignore')

    ustr = unicode
    uchr = unichr
    from urlparse import urlparse
    from urllib2 import urlopen
    from httplib import HTTPConnection
    file = None
    _fake_stdio = io.BytesIO  # Only for tests to capture std{out,err}
else:
    import configparser
    _read_config = configparser.SafeConfigParser.read_file
    ustr = str
    uchr = chr
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from http.client import HTTPConnection
    _fake_stdio = io.StringIO  # Only for tests to capture std{out,err}

configparser = configparser
input = input


def isbasestr(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str) or isinstance(obj, bytes)
