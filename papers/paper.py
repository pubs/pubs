import os
import unicodedata
import re

from pybtex.database import Entry, BibliographyData

import files
import color
import pretty


DEFAULT_TYPE = 'article'

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


class NoDocumentFile(Exception):
    pass


class Paper(object):
    """Paper class. The object is responsible for the integrity of its own
    data, and for loading and writing it to disc.

    The object uses a pybtex.database.BibliographyData object to store
    biblography data and an additional dictionary to store meta data.
    """

    @classmethod
    def load(cls, bibpath, metapath):
        bib_data = files.load_externalbibfile(bibpath)
        metadata = files.read_yamlfile(metapath)
        # Extract first entry (supposed to be the only one)
        first_key = bib_data.entries.keys()[0]
        first_entry = bib_data.entries[first_key]
        p = Paper(bibentry=first_entry, metadata=metadata, citekey=first_key)
        return p

#    @classmethod
#    def from_bibpdffiles(cls, pdfpath, bibpath):
#        bib_data = cls.import_bibdata(bibpath)
#        name, meta = cls.create_meta(bib_data, pdfpath=pdfpath)
#        p = Paper(name, bib_data = bib_data, metadata = meta)
#
#        return p

    def __init__(self, bibentry=None, metadata=None, citekey=None):
        if not bibentry:
            bibentry = Entry(DEFAULT_TYPE)
        self.bibentry = bibentry
        if not metadata:
            metadata = Paper.create_meta()
        self.metadata = metadata
        self.citekey = citekey

    def __eq__(self, other):
        return (type(other) is Paper
            and self.bibentry == other.bibentry
            and self.metadata == other.metadata
            and self.citekey == other.citekey)

    def __repr__(self):
        return 'Paper(%s, %s, %s)' % (
                self.citekey, self.bibentry, self.metadata)

    def __str__(self):
        return self.__repr__()

    # TODO add mechanism to verify keys (15/12/2012)

    def has_file(self):
        """Whether there exist a document file for this entry.
        """
        return self.metadata['path'] is not None

    def get_file_path(self):
        if self.has_file():
            return self.metadata['path']
        else:
            raise NoDocumentFile

    def check_file(self):
        return files.check_file(self.get_file_path())

    def generate_citekey(self):
        """Generate a citekey from bib_data.

        Raises:
            KeyError if no author nor editor is defined.
        """
        author_key = 'author'
        if not 'author' in self.bibentry.persons:
            author_key = 'editor'
        try:
            first_author = self.bibentry.persons[author_key][0]
        except KeyError:
            raise(ValueError,
                    'No author or editor defined: cannot generate a citekey.')
        try:
            year = self.bibentry.fields['year']
        except KeyError:
            year = ''
        citekey = u'{}{}'.format(u''.join(first_author.last()), year)
        return str2citekey(citekey)

    def save_to_disc(self, path):
        """Creates a BibliographyData object containing a single entry and
        saves it to disc.
        """
        if self.citekey is None:
            raise(ValueError,
                'No valid citekey initialized. Cannot save paper')
        bibdata = BibliographyData(entries={self.citekey: self.bibentry})
        files.save_bibdata(bibdata, self.citekey, path=path)
        files.save_meta(self.metadata, self.citekey, path=path)
        # TODO move to repo

    @classmethod
    def import_bibdata(cls, bibfile):
        """Import bibligraphic data from a .bibyaml, .bib or .bibtex file"""
        fullbibpath = os.path.abspath(bibfile)
        bib_data = files.load_externalbibfile(fullbibpath)
        print('{}bibliographic data present in {}{}{}'.format(
               color.grey, color.cyan, bibfile, color.end))
        print(pretty.bib_desc(bib_data))
        return bib_data

    @classmethod
    def create_meta(cls, pdfpath=None):
        if pdfpath is None:
            name, fullpdfpath, ext = None, None, None
        else:
            fullpdfpath = os.path.abspath(pdfpath)
            files.check_file(fullpdfpath)
            name, ext = files.name_from_path(pdfpath)
        meta = {}
        meta['filename'] = name  # TODO remove ?
        meta['extension'] = ext
        meta['path'] = fullpdfpath
        meta['notes'] = []
        return meta
