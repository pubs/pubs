from __future__ import unicode_literals

from ..paper import Paper
from .. import repo
from .. import color

from ..uis import get_ui
from ..endecoder import EnDecoder
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import ModifyEvent


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'search',
        help='search papers in the repository from an author or with given keywords in the title')
    parser.add_argument(
        '-a', '--author', default=False,
        help='search with the author name')
    parser.add_argument(
        '-t', '--title', default=False,
        help='search with the keywords in the title')
    return parser


def command(conf, args):

    ui = get_ui()
    bibfile = args.bibfile

    rp = repo.Repository(conf)
    citekey = args.citekey
    paper = rp.pull_paper(citekey)

    decoder = endecoder.EnDecoder()

    if bibfile is None:
        if args.doi is None and args.isbn is None and args.arxiv is None:
            bibentry = bibentry_from_editor(conf, ui)
        else:
            bibentry = bibentry_from_api(args, ui)
    else:
        bibentry_raw = content.get_content(bibfile, ui=ui)
        bibentry = decoder.decode_bibdata(bibentry_raw)
        if bibentry is None:
            ui.error('invalid bibfile {}.'.format(bibfile))

    # citekey

    citekey = args.citekey
    if citekey is None:
        citekey = rp.unique_citekey(base_key, bibentry)

    p = paper.Paper.from_bibentry(bibentry, citekey=citekey)

    ui.message('{}'.format(pretty.paper_oneliner(p, max_authors=conf['main']['max_authors'])))
