import os
import unicodedata
import re

import files
import color
import pretty


CONTROL_CHARS = ''.join(map(unichr, range(0, 32) + range(127, 160)))
CITEKEY_FORBIDDEN_CHARS = '@\'\\,#}{~%/'  # '/' is OK for bibtex but forbidden
# here since we transform citekeys into filenames
CITEKEY_EXCLUDE_RE = re.compile('[%s]'
        % re.escape(CONTROL_CHARS + CITEKEY_FORBIDDEN_CHARS))


def str2citekey(s):
    return CITEKEY_EXCLUDE_RE.sub('', s)


class NoDocumentFile(Exception):
    pass


class Paper(object):
    """Paper class. The object is responsible for the integrity of its own data,
    and for loading and writing it to disc.
    """

    @classmethod
    def from_disc(cls, name, citekey = None):
        bib_data = files.load_bibdata(name)
        metadata = files.load_meta(name)
        p = Paper(name, bib_data = bib_data, metadata = metadata,
                        citekey = citekey)
        return p

    @classmethod
    def from_bibpdffiles(cls, pdfpath, bibpath):
        bib_data = cls.import_bibdata(bibpath)
        name, meta = cls.create_meta(bib_data, pdfpath=pdfpath)
        p = Paper(name, bib_data = bib_data, metadata = meta)

        return p

    def __init__(self, bib_data = None, metadata = None,
                       citekey = None):
        self.citekey  = citekey
        self.bib_data = bib_data
        self.metadata = metadata

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
        if not 'author' in self.bib_data.persons:
            author_key = 'editor'
        try:
            first_author = self.bib_data.persons[author_key][0]
        except KeyError:
            raise(ValueError,
                    'No author or editor defined: cannot generate a citekey.')
        try:
            year = entry.fields['year']
        except KeyError:
            year = ''
        prefix = u'{}{}'.format(first_author.last()[0][:6], year)
        prefix = str2citekey(prefix)
        # Normalize chars and remove non-ascii
        prefix = unicodedata.normalize('NFKD', prefix
                ).encode('ascii', 'ignore')
        letter = 0
        citekey = prefix
        while citekey in self.citekeys and citekey not in allowed:
            citekey = prefix + ALPHABET[letter]
            letter += 1
        return citekey


    def save_to_disc(self):
        files.save_bibdata(self.bib_data, self.citekey)
        files.save_meta(self.metadata, self.citekey)
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
    def create_meta(cls, bib_data, pdfpath=None):

        if pdfpath is None:
            citekey = bib_data.entries.keys()[0]
            # TODO this introduces a bug and a security issue since the name
            # is used to generate a file name that is written. It should be
            # escaped here. (22/10/2012)
            fullpdfpath, ext = None, None
        else:
            fullpdfpath = os.path.abspath(pdfpath)
            files.check_file(fullpdfpath)

            name, ext = files.name_from_path(pdfpath)

        meta = {}

        meta['name'] = name
        meta['extension'] = ext
        meta['path'] = fullpdfpath

        meta['notes'] = []

        return name, meta
