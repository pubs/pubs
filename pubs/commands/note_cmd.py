from .. import repo
from .. import content
from ..uis import get_ui
from ..utils import resolve_citekey


def parser(subparsers):
    parser = subparsers.add_parser('note',
            help='edit the note attached to a paper')
    parser.add_argument('citekey',
            help='citekey of the paper')
    return parser


def command(conf, args):
    """
    """

    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    notepath = rp.databroker.real_notepath(citekey)
    ui.edit_file(notepath, temporary=False)
    rp.close()
