from datetime import datetime

from .. import repo
from .. import pretty
from .. import bibstruct
from ..uis import get_ui


class InvalidQuery(ValueError):
    pass


def parser(subparsers, conf):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('-k', '--citekeys-only', action='store_true',
            default=False, dest='citekeys',
            help='Only returns citekeys of matching papers.')
    parser.add_argument('-i', '--ignore-case', action='store_false',
            default=None, dest='case_sensitive')
    parser.add_argument('-I', '--force-case', action='store_true',
            dest='case_sensitive')
    parser.add_argument('-a', '--alphabetical', action='store_true',
            dest='alphabetical', default=False,
            help='lexicographic order on the citekeys.')
    parser.add_argument('--no-docs', action='store_true',
            dest='nodocs', default=False,
            help='list only pubs without attached documents.')

    parser.add_argument('query', nargs='*',
            help='Paper query ("author:Einstein", "title:learning", "year:2000" or "tags:math")')
    return parser


def date_added(p):
    return p.added or datetime(1, 1, 1)


def command(conf, args):
    ui = get_ui()
    rp = repo.Repository(conf)
    papers = filter(lambda p: filter_paper(p, args.query,
                                           case_sensitive=args.case_sensitive),
                    rp.all_papers())
    if args.nodocs:
        papers = [p for p in papers if p.docpath is None]
    if args.alphabetical:
        papers = sorted(papers, key=lambda p: p.citekey)
    else:
        papers = sorted(papers, key=date_added)
    if len(papers) > 0:
        ui.message('\n'.join(
            pretty.paper_oneliner(p, citekey_only=args.citekeys)
            for p in papers))

    rp.close()


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


def _lower(s, lower=True):
    return s.lower() if lower else s


def _check_author_match(paper, query, case_sensitive=False):
    """Only checks within last names."""
    if not 'author' in paper.bibdata:
        return False
    return any([query in _lower(bibstruct.author_last(p), lower=(not case_sensitive))
                for p in paper.bibdata['author']])



def _check_tag_match(paper, query, case_sensitive=False):
    return any([query in _lower(t, lower=(not case_sensitive))
                for t in paper.tags])


def _check_field_match(paper, field, query, case_sensitive=False):
    return query in _lower(paper.bibdata[field],
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
    elif field in paper.bibdata:
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
