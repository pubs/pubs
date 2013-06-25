# init command

import os

from ..repo import Repository
from .. import configs
from .. import color

def parser(subparsers, config):
    parser = subparsers.add_parser('init',
                                   help="initialize the papers directory")
    parser.add_argument('-p', '--path', default=None,
                        help='path to papers directory (if none, ~/.papers is used)')
    parser.add_argument('-d', '--doc-dir', default=None,
                        help=('path to document directory (if none, documents '
                              'are stored in the same directory)'))
    return parser


def command(config, ui, path, doc_dir):
    """Create a .papers directory"""
    if path is None:
        papersdir = config.get('papers', 'papers-directory')
    else:
        papersdir = os.path.join(os.getcwd(), path)
        configs.add_and_write_option('papers', 'papers-directory', papersdir)
    if os.path.exists(papersdir):
        if len(os.listdir(papersdir)) > 0:
            ui.error('directory {} is not empty.'.format(
                                 color.dye(papersdir, color.filepath)))
            ui.exit()

    ui.print_('Initializing papers in {}.'.format(
              color.dye(papersdir, color.filepath)))
    repo = Repository()
    repo.init(papersdir)  # Creates directories
    repo.save()  # Saves empty repository description