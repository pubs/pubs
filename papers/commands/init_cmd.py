# init command

import os

from ..repo import Repository
from ..color import colored


def parser(subparsers, config):
    parser = subparsers.add_parser('init',
            help="initialize the .papers directory")
    return parser


def command(config, ui):
    """Create a .papers directory"""
    papersdir = os.getcwd() + '/.papers'
    if not os.path.exists(papersdir):
        print('Initializing papers in {}'.format(
               colored(papersdir, 'filepath')))
        repo = Repository()
        repo.init(papersdir)  # Creates directories
        repo.save()  # Saves empty repository description
    else:
        ui.error('papers already present in {}.'.format(
               colored(papersdir, 'filepath')))
        exit(-1)
