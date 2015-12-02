# init command

import os

from ..configs import config
from ..uis import get_ui
from .. import color
from ..repo import Repository
from ..content import system_path, check_directory


def parser(subparsers):
    parser = subparsers.add_parser('init',
                                   help="initialize the pubs directory")
    parser.add_argument('-p', '--pubsdir', default=None,
                        help='path to pubs directory (if none, ~/.ubs is used)')
    parser.add_argument('-d', '--docsdir', default='docsdir://',
                        help=('path to document directory (if not specified, documents will'
                              'be stored in /path/to/pubsdir/doc/)'))
    return parser


def command(args):
    """Create a .pubs directory"""

    ui = get_ui()
    pubsdir = args.pubsdir
    docsdir = args.docsdir

    if pubsdir is None:
        pubsdir = '~/.pubs'

    pubsdir = system_path(pubsdir)

    if check_directory(pubsdir, fail=False) and len(os.listdir(pubsdir)) > 0:
        ui.error('directory {} is not empty.'.format(
            color.dye_err(pubsdir, color.filepath)))
        ui.exit()

    ui.print_out('Initializing pubs in {}'.format(color.dye_out(pubsdir, color.filepath)))

    config().pubsdir = pubsdir
    config().docsdir = docsdir
    config().save()

    Repository(config(), create=True)
