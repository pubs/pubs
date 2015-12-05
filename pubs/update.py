from . import config
from . import uis
from .__init__ import __version__


def update_check(conf):
    """Runs an update if necessary, and return True in that case."""

    code_version = __version__.split('.')
    try:
        repo_version = conf['internal']['version'].split('.')
    except KeyError:
        repo_version = ['0', '5', '0']

    if repo_version > code_version:
        uis.init_ui(config.load_default_conf())
        ui = uis.get_ui()

        ui.warning(
                'Your repository was generated with an newer version'
                ' of pubs (v{}) than the one you are using (v{}).'
                '\n'.format(repo_version, code_version) +
                'You should not use pubs until you install the '
                'newest version.')
        sys.exit()

    elif repo_version < code_version:
        return update(conf, code_version, repo_version)

    return False

def update(conf, code_version, repo_version):
    """Runs an update if necessary, and return True in that case."""

    if repo_version == ['0', '5', '0']: # we need to update
        default_conf = config.load_default_conf()
        uis.init_ui(config.load_default_conf())
        ui = uis.get_ui()

        for key in ['pubsdir', 'docsdir', 'edit_cmd', 'open_cmd']:
            default_conf['main'][key] = conf['pubs'][key]
        if conf['pubs']['import_move']:
            default_conf['main']['add_doc'] = 'move'
        elif conf['pubs']['import_copy']:
            default_conf['main']['add_doc'] = 'copy'
        else:
            default_conf['main']['add_doc'] = 'link'

        backup_path = config.get_confpath() + '.old'
        config.save_conf(conf, path=backup_path)
        config.save_conf(default_conf)

        ui.warning(
            'Your configuration file has been updated. '
            'The old file has been moved to `{}`. '.format(backup_path) +
            'Some, but not all, of your settings has been transferred '
            'to the new file.\n'
            'You can inspect and modify your configuration '
            ' using the `pubs config` command.'
        )

        return True
    return False
