# init command

import os

from ..repo import Repository
from ..configs import config
from .. import color
from .. import files

def parser(subparsers):
    parser = subparsers.add_parser('init',
                                   help="initialize the papers directory")
    parser.add_argument('-p', '--path', default=None,
                        help='path to papers directory (if none, ~/.papers is used)')
    parser.add_argument('-d', '--doc-dir', default=None,
                        help=('path to document directory (if none, documents '
                              'are stored in the same directory)'))
    return parser


def command(ui, path, doc_dir):
    """Create a .papers directory"""
    if path is not None:
        config().papers_dir = files.clean_path(os.getcwd(), path)
    ppd = config().papers_dir
    if os.path.exists(ppd) and len(os.listdir(ppd)) > 0:
            ui.error('directory {} is not empty.'.format(
                                 color.dye(ppd, color.filepath)))
            ui.exit()

    ui.print_('Initializing papers in {}.'.format(
              color.dye(ppd, color.filepath)))

    repo = Repository(config(), load = False)
    repo.save()
    config().save()
