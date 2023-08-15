from __future__ import unicode_literals
try:
    import __builtin__
except Exception:
    # Python 3.x
    import builtins
    if 'unicode' not in builtins.__dict__.keys():
        unicode = str

import unicodedata
import re
from string import Formatter

from .p3 import ustr, uchr


# Citekey stuff

TYPE_KEY = 'ENTRYTYPE'

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
    return '/' not in citekey


class CitekeyFormatter(Formatter):
    def __init__(self):
        super(CitekeyFormatter, self).__init__()

    def format_field(self, val, fmt):
        if len(fmt) > 0 and fmt[0] == 'u':
            s = str(val).upper()
            fmt = fmt[1:]
        elif len(fmt) > 0 and fmt[0] == 'l':
            s = str(val).lower()
            fmt = fmt[1:]
        else:
            s = val
        return str2citekey(s.__format__(fmt))

    def get_value(self, key, args, entry):
        if isinstance(key, (str, unicode)):
            okey = key
            if key == 'author' and 'author' not in entry:
                key = 'editor'
            elif key == 'editor' and 'editor' not in entry:
                key = 'author'

            if key == 'author_last_name' and 'author' in entry:
                return author_last(entry['author'][0])
            if key == 'short_title' and 'title' in entry:
                return get_first_word(entry['title'])
            else:
                if key in entry:
                    return entry[key]
                else:
                    raise ValueError(
                        "No {} defined: cannot generate a citekey.".format(okey))
        else:
            raise ValueError('Key must be a str instance')


def get_first_word(title):
    """
    Returns the first word of the title as used in Google Scholar or Arxiv citekeys
    """
    title = re.split(r'[^a-zA-Z0-9]', title)
    word_blacklist = {'and', 'on', 'in', 'of', 'the', 'a', 'an', 'at'}
    word = next((x for x in title if x and x.lower() not in word_blacklist), None)
    return word


def generate_citekey(bibdata, format_string='{author_last_name}{year}'):
    """ Generate a citekey from bib_data.

        :raise ValueError:  if no author nor editor is defined.
    """
    citekey, entry = get_entry(bibdata)
    citekey = CitekeyFormatter().format(format_string, **entry)
    return citekey


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
