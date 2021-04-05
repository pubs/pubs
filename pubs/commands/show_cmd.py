from __future__ import unicode_literals

from .. import repo
from .. import color

from ..uis import get_ui
from ..endecoder import EnDecoder
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import ModifyEvent
from .. import paper
from .. import pretty


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'show',
        help='print a bibliographic entry on the terminal')
    parser.add_argument(
        'citekey',
        help='citekey of the paper').completer = CiteKeyCompletion(conf)
    return parser

def show(ui, conf, paper):
    ui.message('{}'.format(pretty.paper_oneliner(paper, max_authors=conf['main']['max_authors'])))

def command(conf, args):
    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, conf, args.citekey, ui=ui, exit_on_fail=True)
    paper = rp.pull_paper(citekey)
    show(ui, conf, paper)
    #ui.message('{}'.format(pretty.paper_oneliner(paper, max_authors=conf['main']['max_authors'])))
