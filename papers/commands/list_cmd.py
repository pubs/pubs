from .. import repo
from . import helpers
from ..configs import config
from ..uis import get_ui


class InvalidQuery(ValueError):
    pass


def parser(subparsers):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('-k', '--citekeys-only', action='store_true',
            default=False, dest='citekeys',
            help='Only returns citekeys of matching papers.')
    parser.add_argument('-i', '--ignore-case', action='store_false',
            default=None, dest='case_sensitive')
    parser.add_argument('-I', '--force-case', action='store_true',
             dest='case_sensitive')
    parser.add_argument('query', nargs='*',
            help='Paper query (e.g. "year: 2000" or "tags: math")')
    return parser


def command(args):
    ui = get_ui()
    rp = repo.Repository(config())
    papers = filter(lambda (n, p):
            filter_paper(p, args.query, case_sensitive=args.case_sensitive),
            enumerate(rp.all_papers()))
    ui.print_('\n'.join(
        helpers.paper_oneliner(p, n=n, citekey_only=args.citekeys)
        for n, p in papers))


FIELD_ALIASES = {
    'a': 'author',
    'authors': 'author',
    't': 'title',
    'tags': 'tag',
    }


def _get_field_value(query_block):
    split_block = query_block.split(':')
    if len(split_block) != 2:
        raise InvalidQuery("Invalid query (%s)" % query_block)
    field = split_block[0]
    if field in FIELD_ALIASES:
        field = FIELD_ALIASES[field]
    value = split_block[1]
    return (field, value)


def _lower(string, lower=True):
    if lower:
        return string.lower()
    else:
        return string


def _check_author_match(paper, query, case_sensitive=False):
    """Only checks within last names."""
    if not 'author' in paper.bibentry.persons:
        return False
    return any([query in _lower(name, lower=(not case_sensitive))
                for p in paper.bibentry.persons['author']
                for name in p.last()])


def _check_tag_match(paper, query, case_sensitive=False):
    return any([query in _lower(t, lower=(not case_sensitive))
                for t in paper.tags])


def _check_field_match(paper, field, query, case_sensitive=False):
    return query in _lower(paper.bibentry.fields[field],
                       lower=(not case_sensitive))


def _check_query_block(paper, query_block, case_sensitive=None):
    field, value = _get_field_value(query_block)
    if case_sensitive is None:
        case_sensitive = not value.islower()
    elif not case_sensitive:
            value = value.lower()
    if field == 'tag':
        return _check_tag_match(paper, value, case_sensitive=case_sensitive)
    elif field == 'author':
        return _check_author_match(paper, value, case_sensitive=case_sensitive)
    elif field in paper.bibentry.fields:
        return _check_field_match(paper, field, value,
                                  case_sensitive=case_sensitive)
    else:
        return False


# TODO implement search by type of document
def filter_paper(paper, query, case_sensitive=None):
    """If case_sensitive is not given, only check case if query
    is not lowercase.

    :args query: list of query blocks (strings)
    """
    return all([_check_query_block(paper, query_block,
                                   case_sensitive=case_sensitive)
                for query_block in query])
