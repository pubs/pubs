from __future__ import unicode_literals

from datetime import datetime

from .. import repo
from .. import pretty
from ..uis import get_ui
from ..query import get_paper_filter, QUERY_HELP


def parser(subparsers, conf):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('-k', '--citekeys-only', action='store_true',
                        default=False, dest='citekeys',
                        help='Only returns citekeys of matching papers.')
    parser.add_argument('-i', '--ignore-case', action='store_false',
                        default=None, dest='case_sensitive')
    parser.add_argument('-I', '--force-case', action='store_true',
                        dest='case_sensitive')
    parser.add_argument('--strict', action='store_true', default=False,
                        help='force strict unicode comparison of query')
    parser.add_argument('-a', '--alphabetical', action='store_true',
                        dest='alphabetical', default=False,
                        help='lexicographic order on the citekeys.')
    parser.add_argument('--no-docs', action='store_true',
                        dest='nodocs', default=False,
                        help='list only pubs without attached documents.')
    parser.add_argument('query', nargs='*',
                        help=QUERY_HELP)
    return parser


def date_added(p):
    return p.added or datetime(1, 1, 1)


def command(conf, args):
    ui = get_ui()
    rp = repo.Repository(conf)
    papers = filter(get_paper_filter(args.query,
                                     case_sensitive=args.case_sensitive,
                                     strict=args.strict),
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
