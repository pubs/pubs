from __future__ import unicode_literals

import unicodedata
import re
from string import Formatter

from .p3 import ustr, uchr

# Citekey stuff

TYPE_KEY = 'type'

CONTROL_CHARS = ''.join(map(uchr, list(range(0, 32)) + list(range(127, 160))))
CITEKEY_FORBIDDEN_CHARS = '@\'\\,#}{~%/ '  # '/' is OK for bibtex but forbidden
# here since we transform citekeys into filenames
CITEKEY_EXCLUDE_RE = re.compile(
    '[%s]' % re.escape(CONTROL_CHARS + CITEKEY_FORBIDDEN_CHARS))


def str2citekey(s):
    key = unicodedata.normalize('NFKD', ustr(s)).encode('ascii', 'ignore').decode()
    key = CITEKEY_EXCLUDE_RE.sub('', key)
    # Normalize chars and remove non-ascii
    return key


def check_citekey(citekey):
    if citekey is None or not citekey.strip():
        raise ValueError("Empty citekeys are not valid")


def verify_bibdata(bibdata):
    if bibdata is None or len(bibdata) == 0:
        raise ValueError("no valid bibdata")
    if len(bibdata) > 1:
        raise ValueError("ambiguous: multiple entries in the bibdata.")


def get_entry(bibdata):
    verify_bibdata(bibdata)
    for e in bibdata.items():
        return e


def extract_citekey(bibdata):
    citekey, entry = get_entry(bibdata)
    return citekey


def author_last(author_str):
    """ Return the last name of the author """
    return author_str.split(',')[0]


def valid_citekey(citekey):
    """Return if a citekey is a valid filename or not"""
    # FIXME: a bit crude, but efficient for now (and allows unicode citekeys)
    return not '/' in citekey

class CitekeyFormatter(Formatter):
    def __init__(self):
        super(CitekeyFormatter, self).__init__()

    def get_value(self, key, args, kwds):
        if len(args) == 0:
            raise ValueError('Must pass bibtex entry to the format method')
        entry = args[0]
        if isinstance(key, str):
            okey = key
            if key == 'author' and not 'author' in entry:
                key = 'editor'
            elif key == 'editor' and not 'editor' in entry:
                key = 'author'

            if key == 'first_word' and 'title' in entry:
                return CitekeyFormatter._U(entry['title'].split(' ')[0])
            if key == 'author_last_name' and 'author' in entry:
                return CitekeyFormatter._U(author_last(entry['author'][0]))
            else:
                if key in entry:
                    return CitekeyFormatter._U(entry[key])
                else:
                    raise ValueError(
                        "No {} defined: cannot generate a citekey.".format(okey))

    class _U(str):
        def __init__(self, value):
            super(CitekeyFormatter._U, self).__init__(value)

        def __format__(self, fmt):
            val = self
            if len(fmt) > 0 and fmt[0] == 'u':
                s = val.upper()
                fmt = fmt[1:]
            elif len(fmt) > 0 and fmt[0] == 'l':
                s = val.lower()
                fmt = fmt[1:]
            else:
                s = str(val)
            return s.__format__(fmt)


def generate_citekey(bibdata, format_string='{author_last_name:l}{year}{first_word:l}'):
    """ Generate a citekey from bib_data.

        :raise ValueError:  if no author nor editor is defined.
    """
    citekey, entry = get_entry(bibdata)
    citekey = CitekeyFormatter().format(format_string, entry)
    return str2citekey(citekey)


def extract_docfile(bibdata, remove=False):
    """ Try extracting document file from bib data.
        Returns None if not found.

        :param remove: remove field after extracting information (default: False)
    """
    try:
        if 'file' in bibdata:
            field = bibdata['file']
            # Check if this is mendeley specific
            for f in field.split(':'):
                if len(f) > 0:
                    break
            if remove:
                bibdata.pop('file')
            # This is a hck for Mendeley. Make clean
            if f[0] != '/':
                f = '/' + f
            return f
        if 'attachments' in bibdata:
            return bibdata['attachments']
        if 'pdf' in bibdata:
            return bibdata['pdf']
    except (KeyError, IndexError):
        return None
