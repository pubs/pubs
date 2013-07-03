from .. import pretty
from .. import repo
from .. import color
from . import helpers
from ..configs import config


def parser(subparsers):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('-k', '--citekeys-only', action='store_true',
            default=False, dest='citekeys',
            help='Only returns citekeys of matching papers.')
    parser.add_argument('query', nargs='*',
            help='Paper query (e.g. "year: 2000" or "tags: math")')
    return parser


def command(args):

    ui = args.ui
    citekeys = args.citekeys
    query = args.query

    rp = repo.Repository(config())
    papers = [(n, p) for n, p in enumerate(rp.all_papers())
              if test_paper(query, p)]
    ui.print_('\n'.join(helpers.paper_oneliner(p, n = n, citekey_only = citekeys) for n, p in papers))


# TODO author is not implemented, should we do it by last name only or more
# complex
# TODO implement search by type of document
def test_paper(query_string, p):
    for test in query_string:
        tmp = test.split(':')
        if len(tmp) != 2:
            raise ValueError('command not valid')

        field = tmp[0]
        value = tmp[1]

        if field in ['tags', 't']:
            if value not in p.tags:
                return False
        elif field in ['author', 'authors', 'a']:  # that is the very ugly
            if not 'author' in p.bibentry.persons:
                return False
            a = False
            for p in p.bibentry.persons['author']:
                if value in p.last()[0]:
                    a = True
            return a
        elif field in p.bibentry.fields:
                if value not in p.bibentry.fields[field]:
                    return False
        else:
            return False
    return True
