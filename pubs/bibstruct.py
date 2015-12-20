from __future__ import unicode_literals

import unicodedata
import re

from .p3 import ustr, uchr

# Citekey stuff

TYPE_KEY = 'type'

CONTROL_CHARS = ''.join(map(uchr, list(range(0, 32)) + list(range(127, 160))))
CITEKEY_FORBIDDEN_CHARS = '@\'\\,#}{~%/ '  # '/' is OK for bibtex but forbidden
# here since we transform citekeys into filenames
CITEKEY_EXCLUDE_RE = re.compile('[%s]'
        % re.escape(CONTROL_CHARS + CITEKEY_FORBIDDEN_CHARS))

def str2citekey(s):
    key = unicodedata.normalize('NFKD', ustr(s)).encode('ascii', 'ignore').decode()
    key = CITEKEY_EXCLUDE_RE.sub('', key)
    # Normalize chars and remove non-ascii
    return key

def check_citekey(citekey):
    # TODO This is not the right way to test that (17/12/2012)
    if ustr(citekey) != str2citekey(citekey):
        raise ValueError(u"Invalid `{}` citekey; ".format(citekey) +
                         u"utf-8 citekeys are not supported yet.\n"
                         u"See https://github.com/pubs/pubs/issues/28 for details.")

def verify_bibdata(bibdata):
    if bibdata is None or len(bibdata) == 0:
        raise ValueError(u"no valid bibdata")
    if len(bibdata) > 1:
        raise ValueError(u"ambiguous: multiple entries in the bibdata.")

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

def generate_citekey(bibdata):
    """ Generate a citekey from bib_data.

        :param generate:  if False, return the citekey defined in the file,
                          does not generate a new one.
        :raise ValueError:  if no author nor editor is defined.
    """
    citekey, entry = get_entry(bibdata)
    author_key = 'author' if 'author' in entry else 'editor'
    try:
        first_author = entry[author_key][0]
    except KeyError:
        raise ValueError(
                u"No author or editor defined: cannot generate a citekey.")
    try:
        year = entry['year']
    except KeyError:
        year = ''
    citekey = u'{}{}'.format(u''.join(author_last(first_author)), year)

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
