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
        ui.print_('You papers repository is up-to-date.')
        sys.exit(0)
    elif repo_version > code_version:
        ui.print_('Your repository was generated with an newer version of papers.\n'
                  'You should not use papers until you install the newest version.')
        sys.exit(0)
    else:
        msg = ("You should backup the paper directory {} before continuing."
               "Continue ?").format(color.dye(config().papers_dir, color.filepath))
        sure = ui.input_yn(question=msg, default='n')
        if not sure:
            sys.exit(0)

        if repo_version == 1:
            rp = repo.Repository(config())
            for p in rp.all_papers():
                tags = set(p.metadata['tags'])
                tags = tags.union(p.metadata['labels'])
                p.metadata.pop('labels', [])
                rp.save_paper(p)
            repo_version = 2


        if repo_version == 2:
            # update config
            cfg_update = [('papers-directory', 'papers_dir'),
                          ('open-cmd', 'open_cmd'),
                          ('edit-cmd', 'edit_cmd'),
                          ('import-copy', 'import_copy'),
                          ('import-move', 'import_move'),
                         ]
            for old, new in cfg_update:
                try:
                    config()._cfg.set('papers', new, config()._cfg.get('papers', old))
                    config()._cfg.remove_option('papers', old)
                except Exception:
                    pass
            config().save()
            repo_version = 3

        config().version = repo_version
        config().save()
