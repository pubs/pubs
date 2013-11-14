import copy
import collections

from . import bibstruct

DEFAULT_META = collections.OrderedDict([('docfile', None), ('tags', set()), ('notes', [])])
DEFAULT_META = {'docfile': None, 'tags': set(), 'notes': []}

class Paper(object):
    """ Paper class. The object is responsible for the integrity of its data

        The object is not responsible of any disk i/o.
        self.bibdata is a pybtex.database.BibliographyData object
        self.metadata is a dictionary
    """

    def __init__(self, bibdata, citekey=None, metadata=None):
        self.citekey  = citekey
        self.metadata = metadata
        self.bibdata  = bibdata

        _, self.bibentry = bibstruct.get_entry(self.bibdata)

        if self.metadata is None:
            self.metadata = copy.deepcopy(DEFAULT_META)
        if self.citekey is None:
            self.citekey = bibstruct.extract_citekey(self.bibdata)                            
            bibstruct.check_citekey(self.citekey)

    def __eq__(self, other):
        return (isinstance(self, Paper) and type(other) is type(self)
            and self.bibdata  == other.bibdata
            and self.metadata == other.metadata
            and self.citekey  == other.citekey)

    def __repr__(self):
        return 'Paper(%s, %s, %s)' % (
                self.citekey, self.bibentry, self.metadata)

    def deepcopy(self):
        return Paper(citekey =self.citekey,
                     metadata=copy.deepcopy(self.metadata),
                     bibdata=copy.deepcopy(self.bibdata))

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
        return self.metadata.setdefault('tags', set())

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
