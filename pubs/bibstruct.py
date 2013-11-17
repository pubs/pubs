import unicodedata
import re

    # citekey stuff

CONTROL_CHARS = ''.join(map(unichr, range(0, 32) + range(127, 160)))
CITEKEY_FORBIDDEN_CHARS = '@\'\\,#}{~%/'  # '/' is OK for bibtex but forbidden
# here since we transform citekeys into filenames
CITEKEY_EXCLUDE_RE = re.compile('[%s]'
        % re.escape(CONTROL_CHARS + CITEKEY_FORBIDDEN_CHARS))

def str2citekey(s):
    key = unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')
    key = CITEKEY_EXCLUDE_RE.sub('', key)
    # Normalize chars and remove non-ascii
    return key

def check_citekey(citekey):
    # TODO This is not the right way to test that (17/12/2012)
    if unicode(citekey) != str2citekey(citekey):
        raise ValueError("Invalid citekey: %s" % citekey)

def verify_bibdata(bibdata):
    if not hasattr(bibdata, 'entries') or len(bibdata.entries) == 0:
        raise ValueError('no entries in the bibdata.')
    if len(bibdata.entries) > 1:
        raise ValueError('ambiguous: multiple entries in the bibdata.')

def get_entry(bibdata):
    verify_bibdata(bibdata)
    return bibdata.entries.iteritems().next()

def extract_citekey(bibdata):
    verify_bibdata(bibdata)
    citekey, entry = get_entry(bibdata)
    return citekey

def generate_citekey(bibdata):
    """ Generate a citekey from bib_data.

        :param generate:  if False, return the citekey defined in the file,
                          does not generate a new one.
        :raise ValueError:  if no author nor editor is defined.
    """
    citekey, entry = get_entry(bibdata)

    author_key = 'author' if 'author' in entry.persons else 'editor'
    try:
        first_author = entry.persons[author_key][0]
    except KeyError:
        raise ValueError(
                'No author or editor defined: cannot generate a citekey.')
    try:
        year = entry.fields['year']
    except KeyError:
        year = ''
    citekey = u'{}{}'.format(u''.join(first_author.last()), year)

    return str2citekey(citekey)

def extract_docfile(bibdata, remove=False):
    """ Try extracting document file from bib data.
        Returns None if not found.

        :param remove: remove field after extracting information (default: False)
    """
    citekey, entry = get_entry(bibdata)

    try:
        if 'file' in entry.fields:
            field = entry.fields['file']
            # Check if this is mendeley specific
            for f in field.split(':'):
                if len(f) > 0:
                    break
            if remove:
                entry.fields.pop('file')
            # This is a hck for Mendeley. Make clean
            if f[0] != '/':
                f = '/' + f
            return f
        if 'attachments' in entry.fields:
            return entry.fields['attachments']
    except (KeyError, IndexError):
        return None
