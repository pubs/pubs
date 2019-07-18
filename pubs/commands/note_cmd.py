from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import NoteEvent


def parser(subparsers, conf):
    parser = subparsers.add_parser('note',
                                   help='edit the note attached to a paper')
    parser.add_argument('citekey', help='citekey of the paper',
                        ).completer = CiteKeyCompletion(conf)
    parser.add_argument('-a', '--append', help='append a line of text to the notes file', default=None)
    return parser


def command(conf, args):

    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    append = args.append
    notepath = rp.databroker.real_notepath(citekey, rp.conf['main']['note_extension'])
    if append is None:
        ui.edit_file(notepath, temporary=False)
    else:
        with open(notepath, 'a') as fd:
            fd.write(append)
    NoteEvent(citekey).send()
    rp.close()
