# init command

import os

from ..repo import Repository
from .. import color


def parser(subparsers, config):
    parser = subparsers.add_parser('init',
            help="initialize the .papers directory")
    return parser


def command(config):
    """Create a .papers directory"""
    papersdir = os.getcwd() + '/.papers'
    if not os.path.exists(papersdir):
        print('{}initializing papers in {}{}{}'.format(
               color.grey, color.cyan, papersdir, color.end))
        repo = Repository(papersdir=papersdir)
        repo.init()  # Creates directories
        repo.save()  # Saves empty repository description
    else:
        print('{}error {} : papers already present in {}{}{}'.format(
               color.red, color.grey, color.cyan, papersdir, color.end))
        exit(-1)
