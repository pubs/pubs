from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import NoteEvent
from ..content import write_file


def parser(subparsers, conf):
    parser = subparsers.add_parser('note',
                                   help='edit the note attached to a paper')
    parser.add_argument('citekey', help='citekey of the paper',
                        ).completer = CiteKeyCompletion(conf)
    parser.add_argument('-a', '--append',
                        help='append a line of text to the notes file', default=None)
    return parser


def command(conf, args):

    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    latestnote = '{TXT}\n'.format(TXT=args.append)
    notepath = rp.databroker.real_notepath(citekey, rp.conf['main']['note_extension'])
    if latestnote is None:
        ui.edit_file(notepath, temporary=False)
    else:
        write_file(notepath, latestnote, 'a')
    NoteEvent(citekey).send()
    rp.close()
