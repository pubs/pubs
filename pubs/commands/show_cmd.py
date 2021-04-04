from __future__ import unicode_literals

from .. import repo
from .. import color

from ..uis import get_ui
from ..endecoder import EnDecoder
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import ModifyEvent
from .. import paper


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'show',
        help='print a bibliographic entry on the terminal')
    parser.add_argument(
        'citekey',
        help='citekey of the paper').completer = CiteKeyCompletion(conf)
    return parser


def command(conf, args):

    ui = get_ui()
    rp = repo.Repository(conf)
    bibfile = args.bibfile
    #paper = rp.pull_paper(citekey)
    decoder = endecoder.EnDecoder()
    citekey = args.citekey
    bibentry_raw = content.get_content(bibfile, ui=ui)
    bibentry = decoder.decode_bibdata(bibentry_raw)

    p = paper.Paper.from_bibentry(bibentry, citekey=citekey)

    ui.message('{}'.format(pretty.paper_oneliner(p, max_authors=conf['main']['max_authors'])))
