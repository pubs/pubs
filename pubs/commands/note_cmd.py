from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion


def parser(subparsers, conf):
    parser = subparsers.add_parser('note',
                                   help='edit the note attached to a paper')
    parser.add_argument('citekey', help='citekey of the paper',
                        ).completer = CiteKeyCompletion(conf)
    return parser


def command(conf, args):

    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    notepath = rp.databroker.real_notepath(citekey, rp.conf['main']['note_extension'])
    ui.edit_file(notepath, temporary=False)
    rp.close()
