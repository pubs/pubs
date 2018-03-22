# init command
from __future__ import unicode_literals

import os


from ..uis import get_ui
from .. import color
from ..repo import Repository
from ..content import system_path, check_directory
from .. import config


def parser(subparsers, conf):
    parser = subparsers.add_parser('init',
                                   help="initialize the pubs directory")
    parser.add_argument('-p', '--pubsdir', default=None,
                        help='directory where to put the pubs repository (if none, ~/.pubs is used)')
    parser.add_argument('-d', '--docsdir', default='docsdir://',
                        help=('path to document directory (if not specified, documents will'
                              'be stored in /path/to/pubsdir/doc/)'))
    return parser


def command(conf, args):
    """Create a .pubs directory"""

    ui = get_ui()
    pubsdir = args.pubsdir
    docsdir = args.docsdir

    if pubsdir is None:
        pubsdir = '~/.pubs'

    pubsdir = system_path(pubsdir)

    if check_directory(pubsdir, fail=False) and len(os.listdir(pubsdir)) > 0:
        ui.error('Directory {} is not empty.'.format(
            color.dye_err(pubsdir, 'filepath')))
        ui.exit()

    ui.message('Initializing pubs in {}'.format(color.dye_out(pubsdir, 'filepath')))

    conf['main']['pubsdir'] = pubsdir
    conf['main']['docsdir'] = docsdir
    conf['main']['open_cmd'] = config.default_open_cmd()
    conf = config.post_process_conf(conf)
    config.save_conf(conf)

    Repository(conf, create=True)
