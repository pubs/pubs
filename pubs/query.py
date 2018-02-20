import unicodedata

from bibtexparser.latexenc import latex_to_unicode

from . import bibstruct


QUERY_HELP = ('Paper query ("author:Einstein", "title:learning",'
              '"year:2000", "year:2000-2010", or "tags:math")')


FIELD_ALIASES = {
    'a': 'author',
    'authors': 'author',
    't': 'title',
    'tags': 'tag',
    'y': 'year',
}


class InvalidQuery(ValueError):
    pass


class QueryFilter(object):
    """Filter function for papers built from a given query.

    :param case_sensitive: forces case (in)sensitivity; default is to
        only be sensitive if query contains uppercase
    :param strict: if set to True, compares the raw unicode without
        interpreting latex commands, normalizing unicode, or ignoring case.
        (Overrides the case_sensitive parameter.)
    """

    def __init__(self, query, case_sensitive=None, strict=False):
        if case_sensitive is None:
            case_sensitive = not query.islower()
        self.case = case_sensitive
        self.strict = strict
        self.query = self._normalize(query)

    def __call__(self, paper):
        raise NotImplementedError

    def _is_query_in(self, field_value):
        return self.query in self._normalize(field_value)

    def _normalize(self, s):
        if self.strict:
            return s
        else:
            s = unicodedata.normalize('NFC', latex_to_unicode(s))
            # Note: in theory latex_to_unicode also normalizes
            return s if self.case else s.lower()


class FieldFilter(QueryFilter):
    """Generic filter of form `query in paper['field']`"""

    def __init__(self, field, query, case_sensitive=None, strict=False):
        super(FieldFilter, self).__init__(query, case_sensitive=case_sensitive,
                                          strict=strict)
        self.field = field

    def __call__(self, paper):
        return (self.field in paper.bibdata and
                self._is_query_in(paper.bibdata[self.field]))


class AuthorFilter(QueryFilter):

    def __call__(self, paper):
        """Only checks within last names."""
        if 'author' not in paper.bibdata:
            return False
        else:
            return any([self._is_query_in(bibstruct.author_last(author))
                        for author in paper.bibdata['author']])


class TagFilter(QueryFilter):

    def __call__(self, paper):
        return any([self._is_query_in(t) for t in paper.tags])


class YearFilter(QueryFilter):
    """Note: a query like `year:` or `year:-` would match any paper
       whose year field is set and can be converted to an int.
    """

    def __init__(self, query):
        split = query.split('-')
        self.start = self._str_to_year(split[0])
        if len(split) == 1:
            self.end = self.start
        elif len(split) == 2:
            self.end = self._str_to_year(split[1])
        if (len(split) > 2 or (
                self.start is not None and
                self.end is not None and
                self.start > self.end)):
            raise ValueError('Invalid year range "{}"'.format(query))

    def __call__(self, paper):
        """Only checks within last names."""
        if 'year' not in paper.bibdata:
            return False
        else:
            try:
                year = int(paper.bibdata['year'])
                return ((self.start is None or year >= self.start) and
                        (self.end is None or year <= self.end))
            except ValueError:
                return False

    @staticmethod
    def _str_to_year(s):
        try:
            return int(s) if s else None
        except ValueError:
            raise ValueError('Invalid year "{}"'.format(s))


def _get_field_value(query_block):
    split_block = query_block.split(':')
    if len(split_block) != 2:
        raise InvalidQuery("Invalid query (%s)" % query_block)
    field = split_block[0]
    if field in FIELD_ALIASES:
        field = FIELD_ALIASES[field]
    value = split_block[1]
    return (field, value)


def _query_block_to_filter(query_block, case_sensitive=None, strict=False):
    field, value = _get_field_value(query_block)
    if field == 'tag':
        return TagFilter(value, case_sensitive=case_sensitive, strict=strict)
    elif field == 'author':
        return AuthorFilter(value, case_sensitive=case_sensitive,
                            strict=strict)
    elif field == 'year':
        return YearFilter(value)
    else:
        return FieldFilter(field, value, case_sensitive=case_sensitive,
                           strict=strict)


# TODO implement search by type of document
def get_paper_filter(query, case_sensitive=None, strict=False):
    """If case_sensitive is not given, only check case if query
    is not lowercase.

    :args query: list of query blocks (strings)
    """
    filters = [_query_block_to_filter(query_block,
                                      case_sensitive=case_sensitive,
                                      strict=strict)
               for query_block in query]
    return lambda paper: all([f(paper) for f in filters])
