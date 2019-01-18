import copy
from dateutil.parser import parse as datetime_parse

from bibtexparser.customization import convert_to_unicode

from . import bibstruct
from .p3 import ustr


DEFAULT_META = {'docfile': None, 'tags': set()}


def _clean_metadata(metadata):
    meta = copy.deepcopy(DEFAULT_META)
    meta.update(metadata or {})  # handles None metadata
    meta['tags'] = set(meta.get('tags', []))  # tags should be a set
    if 'added' in meta and isinstance(meta['added'], ustr):
        meta['added'] = datetime_parse(meta['added'])
    return meta


class Paper(object):
    """ Paper class.

        The object is not responsible of any disk I/O.
        self.bibdata  is a dictionary of bibligraphic fields
        self.metadata is a dictionary

        The paper class provides methods to access the fields for its metadata
        in a pythonic manner.
    """

    def __init__(self, citekey, bibdata, metadata=None):
        self.citekey = citekey
        self.metadata = _clean_metadata(metadata)
        self.bibdata = bibdata
        bibstruct.check_citekey(self.citekey)

    def __eq__(self, other):
        return (isinstance(self, Paper) and type(other) is type(self)
            and self.bibdata  == other.bibdata
            and self.metadata == other.metadata
            and self.citekey  == other.citekey)

    def __repr__(self):
        return 'Paper(%s, %s, %s)' % (
                self.citekey, self.bibdata, self.metadata)

    def __deepcopy__(self, memo):
        return Paper(citekey=self.citekey,
                     metadata=copy.deepcopy(self.metadata, memo),
                     bibdata=copy.deepcopy(self.bibdata, memo))

    def __copy__(self):
        return Paper(citekey=self.citekey,
                     metadata=self.metadata,
                     bibdata=self.bibdata)

    def deepcopy(self):
        return self.__deepcopy__({})

        # docpath

    @property
    def bibentry(self):
        return {self.citekey: self.bibdata}

    @property
    def docpath(self):
        return self.metadata.get('docfile', '')

    @docpath.setter
    def docpath(self, path):
        """Does not verify if the path exists."""
        self.metadata['docfile'] = path

        # tags

    @property
    def tags(self):
        return self.metadata['tags']

    @tags.setter
    def tags(self, value):
        if not hasattr(value, '__iter__'):
            raise ValueError('tags must be iterables')
        self.metadata['tags'] = set(value)

    def add_tag(self, tag):
        self.tags.add(tag)

    def remove_tag(self, tag):
        """Remove a tag from a paper if present."""
        self.tags.discard(tag)

        # added date

    # Added time, supposed to be stored as datetime object
    @property
    def added(self):
        return self.metadata.get('added', None)

    @added.setter
    def added(self, value):
        self.metadata['added'] = value

    def get_unicode_bibdata(self):
        """Converts latex in bibdata fields to unicode."""
        return convert_to_unicode(self.bibdata)

    @staticmethod
    def from_bibentry(bibentry, citekey=None, metadata=None):
        bibentry_key, bibdata = bibstruct.get_entry(bibentry)
        if citekey is None:
            citekey = bibentry_key
        return Paper(citekey, bibdata, metadata=metadata)
