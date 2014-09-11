import io
import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    _read_config = configparser.SafeConfigParser.readfp

    def input():
        raw_input().decode(sys.stdin.encoding or 'utf8', 'ignore')
    
    # The following has to be a function so that it can be mocked
    # for test_usecase.
    def _get_raw_stdout():
        return sys.stdout

    ustr = unicode
    uchr = unichr
    from urlparse import urlparse
    from urllib2 import urlopen
    from httplib import HTTPConnection
    file = None
    _fake_stdio = io.BytesIO  # Only for tests to capture std{out,err}

    def _get_fake_stdio_ucontent(stdio):
        ustdio = io.TextIOWrapper(stdio)
        ustdio.seek(0)
        return ustdio.read()

else:
    import configparser
    _read_config = configparser.SafeConfigParser.read_file
    ustr = str
    uchr = chr
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from http.client import HTTPConnection

    def _fake_stdio():
        return io.TextIOWrapper(io.BytesIO())  # Only for tests to capture std{out,err}

    def _get_fake_stdio_ucontent(stdio):
        stdio.flush()
        stdio.seek(0)
        return stdio.read()

    # The following has to be a function so that it can be mocked
    # for test_usecase.
    def _get_raw_stdout():
        return sys.stdout.buffer

configparser = configparser
input = input


def isbasestr(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str) or isinstance(obj, bytes)
