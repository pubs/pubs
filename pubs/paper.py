import copy
import collections
import datetime

from . import bibstruct

#DEFAULT_META = collections.OrderedDict([('docfile', None), ('tags', set()), ('added', )])
DEFAULT_META = {'docfile': None, 'tags': set(), 'added': None}

class Paper(object):
    """ Paper class.

        The object is not responsible of any disk I/O.
        self.bibdata  is a dictionary of bibligraphic fields
        self.metadata is a dictionary

        The paper class provides methods to access the fields for its metadata
        in a pythonic manner.
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

        self.metadata['tags'] = set(self.metadata.get('tags', []))

    def __eq__(self, other):
        return (isinstance(self, Paper) and type(other) is type(self)
            and self.bibdata  == other.bibdata
            and self.metadata == other.metadata
            and self.citekey  == other.citekey)

    def __repr__(self):
        return 'Paper(%s, %s, %s)' % (
                self.citekey, self.bibentry, self.metadata)

    def __deepcopy__(self, memo):
        return Paper(citekey =self.citekey,
                     metadata=copy.deepcopy(self.metadata, memo),
                     bibdata=copy.deepcopy(self.bibdata, memo))

    def __copy__(self):
        return Paper(citekey =self.citekey,
                     metadata=self.metadata,
                     bibdata=self.bibdata)

    def deepcopy(self):
        return self.__deepcopy__({})

        # docpath

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

    @property
    def added(self):
        datetime.datetime.strptime(self.metadata['added'], '%Y-%m-%d %H:%M:%S')

    @added.setter
    def added(self, value):
        self.metadata['added'] = value.strftime('%Y-%m-%d %H:%M:%S')
