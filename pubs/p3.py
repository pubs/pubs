import io
import sys

if sys.version_info[0] == 2:
    import cPickle as pickle

    def input():
        return raw_input().decode(sys.stdin.encoding or 'utf8', 'ignore')

    # The following has to be a function so that it can be mocked
    # for test_usecase.
    def _get_raw_stdout():
        return sys.stdout
    def _get_raw_stderr():
        return sys.stderr

    ustr = unicode
    uchr = unichr
    from urlparse import urlparse
    from urllib  import quote_plus
    from urllib2 import urlopen
    from httplib import HTTPConnection
    file = None
    _fake_stdio = io.BytesIO  # Only for tests to capture std{out,err}

    def _get_fake_stdio_ucontent(stdio):
        ustdio = io.TextIOWrapper(stdio)
        ustdio.seek(0)
        return ustdio.read()

else:
    ustr = str
    uchr = chr
    from urllib.parse import urlparse, quote_plus
    from urllib.request import urlopen
    from http.client import HTTPConnection

    # The following has to be a function so that it can be mocked
    # for test_usecase.
    def _get_raw_stdout():
        return sys.stdout.buffer

    def _get_raw_stderr():
        return sys.stderr.buffer

    def _fake_stdio():
        return io.TextIOWrapper(io.BytesIO())  # Only for tests to capture std{out,err}

    def _get_fake_stdio_ucontent(stdio):
        stdio.flush()
        stdio.seek(0)
        return stdio.read()

    import pickle

input = input


def isbasestr(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str) or isinstance(obj, bytes)
