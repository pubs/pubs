import io
import sys
import argparse

from six import b


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

    def u_maybe(s):
        """Convert to unicode, but only if necessary"""
        if isinstance(s, str):
            s = s.decode('utf-8')
        return s

    class StdIO(io.BytesIO):
        """Enable printing the streams received by a BytesIO instance"""
        def __init__(self, *args, **kwargs):
            self.additional_out = kwargs.pop('additional_out')
            super(StdIO, self).__init__(*args, **kwargs)

        def write(self, s):
            if self.additional_out is not None:
                self.additional_out.write(s)

            super(StdIO, self).write(b(s))

    _fake_stdio = StdIO  # Only for tests to capture std{out,err}

    def _get_fake_stdio_ucontent(stdio):

        # ustdio = io.TextIOWrapper(stdio)
        stdio.seek(0)
        return stdio.read()

    # for details, see http://bugs.python.org/issue9779
    class ArgumentParser(argparse.ArgumentParser):
        def _print_message(self, message, file=None):
            """Fixes the lack of a buffer interface in unicode object """
            if message:
                if file is None:
                    file = _sys.stderr
                file.write(message.encode('utf-8'))


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

    def u_maybe(s):
        return s

    class StdIO(io.BytesIO):
        """Enable printing the streams received by a BytesIO instance"""
        def __init__(self, *args, **kwargs):
            self.additional_out = kwargs.pop('additional_out')
            super(StdIO, self).__init__(*args, **kwargs)

        def write(self, s):
            super(StdIO, self).write(s)
            if self.additional_out is not None:
                try:
                    s = s.decode()
                except AttributeError:
                    pass
                self.additional_out.write(s)


    # Only for tests to capture std{out,err}
    def _fake_stdio(additional_out=False):
        return io.TextIOWrapper(StdIO(additional_out=additional_out))

    def _get_fake_stdio_ucontent(stdio):
        stdio.flush()
        stdio.seek(0)
        return stdio.read()

    import pickle

    ArgumentParser = argparse.ArgumentParser

input = input


def isbasestr(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str) or isinstance(obj, bytes)
