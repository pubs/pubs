# init command

import os

from ..repo import Repository
from .. import configs


def parser(subparsers, config):
    parser = subparsers.add_parser('init',
            help="initialize the papers directory")
    parser.add_argument('-p', '--path', default=None,
            help='path to papers directory (if none, ~/.papers is used)')
    parser.add_argument('-d', '--doc-dir', default=None,
            help=('path to document directory '
            '(if none, documents are stored in the same directory)'))
    return parser


def command(config, ui, path, doc_dir):
    """Create a .papers directory"""
    if path is None:
        papersdir = configs.DEFAULT_PAPER_PATH
    else:
        papersdir = os.path.join(os.getcwd(), path)
    if not os.path.exists(papersdir):
        ui.print_('Initializing papers in {}.'.format(
            ui.colored(papersdir, 'filepath')))
        repo = Repository()
        repo.init(papersdir)  # Creates directories
        repo.save()  # Saves empty repository description
    else:
        ui.error('papers already present in {}.'.format(
               ui.colored(papersdir, 'filepath')))
        exit(-1)
