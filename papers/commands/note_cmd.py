from .. import repo
from .. import content
from ..configs import config
from ..uis import get_ui

def parser(subparsers):
    parser = subparsers.add_parser('note',
            help='edit the note attached to a paper')
    parser.add_argument('citekey',
            help='citekey of the paper')
    return parser


def command(args):
    """
    """

    ui = get_ui()


    rp = repo.Repository(config())
    if not rp.databroker.exists(args.citekey):
        ui.error("citekey {} not found".format(args.citekey))
        ui.exit(1)

    notepath = rp.databroker.real_notepath('notesdir://{}.txt'.format(args.citekey))
    content.edit_file(config().edit_cmd, notepath, temporary=False)
