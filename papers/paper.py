import os

import unicodedata
import re
from cStringIO import StringIO
import yaml

from pybtex.database import Entry, BibliographyData, FieldDict, Person

import files


DEFAULT_TYPE = 'article'

CONTROL_CHARS = ''.join(map(unichr, range(0, 32) + range(127, 160)))
CITEKEY_FORBIDDEN_CHARS = '@\'\\,#}{~%/'  # '/' is OK for bibtex but forbidden
# here since we transform citekeys into filenames
CITEKEY_EXCLUDE_RE = re.compile('[%s]'
        % re.escape(CONTROL_CHARS + CITEKEY_FORBIDDEN_CHARS))

BASE_META = {
    'external-document': None,
    'tags': set(),
    'notes': [],
    }


def str2citekey(s):
    key = unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')
    key = CITEKEY_EXCLUDE_RE.sub('', key)
    # Normalize chars and remove non-ascii
    return key


def get_bibentry_from_file(bibfile):
    """Extract first entry (supposed to be the only one) from given file.
    """
    bib_data = files.load_externalbibfile(bibfile)
    first_key = bib_data.entries.keys()[0]
    first_entry = bib_data.entries[first_key]
    return first_key, first_entry


def get_bibentry_from_string(content):
    """Extract first entry (supposed to be the only one) from given file.
    """
    bib_data = files.parse_bibdata(StringIO(content))
    first_key = bib_data.entries.keys()[0]
    first_entry = bib_data.entries[first_key]
    return first_key, first_entry


def copy_person(p):
    return Person(first=p.get_part_as_text('first'),
                  middle=p.get_part_as_text('middle'),
                  prelast=p.get_part_as_text('prelast'),
                  last=p.get_part_as_text('last'),
                  lineage=p.get_part_as_text('lineage'))


def copy_bibentry(entry):
    fd = FieldDict(entry.fields.parent, entry.fields)
    persons = dict([(k, [copy_person(p) for p in v])
                    for k, v in entry.persons.items()])
    return Entry(entry.type, fields=fd, persons=persons)


def get_safe_metadata(meta):
    base_meta = Paper.create_meta()
    if meta is not None:
        base_meta.update(meta)
    base_meta['tags'] = set(base_meta['tags'])
    return base_meta


def get_safe_metadata_from_content(content):
    return get_safe_metadata(yaml.load(content))


def get_safe_metadata_from_path(metapath):
    if metapath is None:
        content = None
    else:
        content = files.read_yamlfile(metapath)
    return get_safe_metadata(content)


def check_citekey(citekey):
    # TODO This is not the right way to test that (17/12/2012)
    if unicode(citekey) != str2citekey(citekey):
        raise(ValueError("Invalid citekey: %s" % citekey))


class NoDocumentFile(Exception):
    pass


class Paper(object):
    """Paper class. The object is responsible for the integrity of its own
    data, and for loading and writing it to disc.

    The object uses a pybtex.database.BibliographyData object to store
    biblography data and an additional dictionary to store meta data.
    """

    def __init__(self, bibentry=None, metadata=None, citekey=None):
        if bibentry is None:
            bibentry = Entry(DEFAULT_TYPE)
        self.bibentry = bibentry
        if metadata is None:
            metadata = Paper.create_meta()
        self.metadata = metadata
        check_citekey(citekey)
        self.citekey = citekey

    def __eq__(self, other):
        return (isinstance(self, Paper) and type(other) is type(self)
            and self.bibentry == other.bibentry
            and self.metadata == other.metadata
            and self.citekey == other.citekey)

    def __repr__(self):
        return 'Paper(%s, %s, %s)' % (
                self.citekey, self.bibentry, self.metadata)

    def __str__(self):
        return self.__repr__()

    # TODO add mechanism to verify keys (15/12/2012)

    def get_external_document_path(self):
        if self.metadata['external-document'] is not None:
            return self.metadata['external-document']
        else:
            raise NoDocumentFile

    def get_document_path(self):
        return self.get_external_document_path()

    def set_external_document(self, docpath):
        fullpdfpath = os.path.abspath(docpath)
        files.check_file(fullpdfpath, fail=True)
        self.metadata['external-document'] = fullpdfpath

    def check_document_path(self):
        return files.check_file(self.get_external_document_path())

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
            raise(ValueError(
                    'No author or editor defined: cannot generate a citekey.'))
        try:
            year = self.bibentry.fields['year']
        except KeyError:
            year = ''
        citekey = u'{}{}'.format(u''.join(first_author.last()), year)
        return str2citekey(citekey)

    def save(self, bib_filepath, meta_filepath):
        """Creates a BibliographyData object containing a single entry and
        saves it to disc.
        """
        if self.citekey is None:
            raise(ValueError(
                'No valid citekey initialized. Cannot save paper'))
        bibdata = BibliographyData(entries={self.citekey: self.bibentry})
        files.save_bibdata(bibdata, bib_filepath)
        files.save_meta(self.metadata, meta_filepath)

    def update(self, key=None, bib=None, meta=None):
        if key is not None:
            check_citekey(key)
            self.citekey = key
        if bib is not None:
            self.bibentry = bib
        if meta is not None:
            self.metadata = meta

    def get_document_file_from_bibdata(self, remove=False):
        """Try extracting document file from bib data.
        Raises NoDocumentFile if not found.

        Parameters:
        -----------
        remove: default: False
            remove field after extracting information
        """
        try:
            field = self.bibentry.fields['file']
            # Check if this is mendeley specific
            for f in field.split(':'):
                if len(f) > 0:
                    break
            if remove:
                self.bibentry.fields.pop('file')
            # This is a hck for Mendeley. Make clean
            if f[0] != '/':
                f = '/' + f
            return f
        except (KeyError, IndexError):
            raise(NoDocumentFile('No file found in bib data.'))

    def copy(self):
        return Paper(bibentry=copy_bibentry(self.bibentry),
                     metadata=self.metadata.copy(),
                     citekey=self.citekey)

    @classmethod
    def load(cls, bibpath, metapath=None):
        key, entry = get_bibentry_from_file(bibpath)
        metadata = get_safe_metadata_from_path(metapath)
        p = Paper(bibentry=entry, metadata=metadata, citekey=key)
        return p

    @classmethod
    def create_meta(cls):
        return BASE_META.copy()

    @classmethod
    def many_from_path(cls, bibpath, fatal=True):
        """Extract list of papers found in bibliographic files in path.
        """
        bibpath = files.clean_path(bibpath)
        if os.path.isdir(bibpath):
            all_files = [os.path.join(bibpath, f) for f in os.listdir(bibpath)
                    if os.path.splitext(f)[-1] in files.BIB_EXTENSIONS]
        else:
            all_files = [bibpath]
        bib_data = [files.load_externalbibfile(f) for f in all_files]
        if fatal:
            return [Paper(bibentry=b.entries[k], citekey=k)
                    for b in bib_data for k in b.entries]
        else:
            papers = []
            for b in bib_data:
                for k in b.entries:
                    try:
                        papers.append(Paper(bibentry=b.entries[k], citekey=k))
                    except ValueError, e:
                        print "Warning, skipping paper (%s)." % e
            return papers


    # tags

    @property
    def tags(self):
        return self.metadata.setdefault('tags', set())

    @tags.setter
    def tags(self, value):
        if not hasattr(value, '__iter__'):
            raise ValueError, 'tags must be iterables'
        self.metadata['tags'] = set(value)

    def add_tag(self, tag):
        self.tags.add(tag)

    def remove_tag(self, tag):
        """Remove a tag from a paper if present."""
        self.tags.discard(tag)


class PaperInRepo(Paper): # TODO document why this class exists (fabien, 2013/06)

    def __init__(self, repo, *args, **kwargs):
        Paper.__init__(self, *args, **kwargs)
        self.repo = repo

    def get_document_path_in_repo(self):
        return self.repo.find_document(self.citekey)

    def get_document_path(self):
        try:
            return self.get_document_path_in_repo()
        except NoDocumentFile:
            return self.get_external_document_path()

    def copy(self):
        return PaperInRepo.from_paper(self.as_paper().copy(), self.repo)

    def as_paper(self):
        return Paper(bibentry=self.bibentry,
                     metadata=self.metadata,
                     citekey=self.citekey)

    @classmethod
    def load(cls, repo, bibpath, metapath=None):
        key, entry = get_bibentry_from_file(bibpath)
        metadata = get_safe_metadata_from_path(metapath)
        p = cls(repo, bibentry=entry, metadata=metadata, citekey=key)
        return p

    @classmethod
    def from_paper(cls, paper, repo):
        return cls(repo, bibentry=paper.bibentry, metadata=paper.metadata,
                   citekey=paper.citekey)
