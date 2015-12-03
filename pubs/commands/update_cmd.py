import sys

from .. import repo
from .. import color
from ..configs import config
from ..uis import get_ui
from ..__init__ import __version__

def parser(subparsers):
    parser = subparsers.add_parser('update', help='update the repository to the lastest format')
    return parser


def command(args):

    ui = get_ui()

    code_version = __version__
    repo_version = int(config().version)

    if repo_version == code_version:
        ui.message('Your pubs repository is up-to-date.')
        sys.exit(0)
    elif repo_version > code_version:
        ui.message('Your repository was generated with an newer version of pubs.\n'
                     'You should not use pubs until you install the newest version.')
        sys.exit(0)
    else:
        msg = ("You should backup the pubs directory {} before continuing."
               "Continue ?").format(color.dye_out(config().papers_dir, color.filepath))
        sure = ui.input_yn(question=msg, default='n')
        if not sure:
            sys.exit(0)


#        config().version = repo_version
#        config().save()
