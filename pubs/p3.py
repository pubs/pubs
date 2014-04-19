import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    import StringIO as io
    input = raw_input
    ustr = unicode
    uchr = unichr
    from urlparse import urlparse
    from urllib2 import urlopen
    from httplib import HTTPConnection
else:
    import configparser
    import io
    ustr = str
    uchr = chr
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from http.client import HTTPConnection

configparser = configparser
io = io
input = input
