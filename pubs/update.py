import shutil

import io
import sys
from . import config
from . import uis
from . import color
from .__init__ import __version__


def update_check(conf, path=None):
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

    elif repo_version <= code_version:
        return update(conf, code_version, repo_version, path=path)

    return False


def update(conf, code_version, repo_version, path=None):
    """Runs an update if necessary, and return True in that case."""
    if path is None:
        path = config.get_confpath()

    if repo_version == ['0', '5', '0']: # we need to update
        default_conf = config.load_default_conf()

        for key in ['pubsdir', 'docsdir', 'edit_cmd', 'open_cmd']:
            if key in conf['pubs']:
                default_conf['main'][key] = conf['pubs'][key]
        if conf.get('import_move'):
            default_conf['main']['add_doc'] = 'move'
        elif conf.get('import_copy'):
            default_conf['main']['add_doc'] = 'copy'
        else:
            default_conf['main']['add_doc'] = 'link'

        backup_path = path + '.old'
        shutil.move(path, backup_path)
        config.save_conf(default_conf)

        uis.init_ui(default_conf)
        ui = uis.get_ui()
        ui.warning(
            'Your configuration file has been updated. '
            'Your old configuration has been moved to `{}`. '.format(color.dye_out(backup_path, 'filepath')) +
            'Some, but not all, of your settings has been transferred '
            'to the new file.\n'
            'You can inspect and modify your configuration '
            ' using the `pubs config` command.'
        )

        return True

    # continuous update while configuration is stabilizing
    if repo_version == ['0', '6', '0'] and repo_version < code_version:
        default_conf = config.load_default_conf()
        for section_name, section in conf.items():
            for key, value in section.items():
                try:
                    default_conf[section_name][key]
                    default_conf[section_name][key] = value
                except KeyError:
                    pass
        # we don't update plugins
        default_conf['plugins']['active'] = conf['plugins']['active']
        for section_name, section in conf['plugins'].items():
            if section_name != 'active':
                default_conf['plugins'][section_name] = section
        default_conf['internal']['version'] = '.'.join(code_version)

        # comparing potential changes
        with open(path, 'r') as f:
            old_conf_text = f.read()
        new_conf_text = io.BytesIO()
        default_conf.write(outfile=new_conf_text)

        if new_conf_text.getvalue() != old_conf_text:

            backup_path = path + '.old'
            shutil.move(path, backup_path)
            default_conf.filename = path
            config.save_conf(default_conf)

            uis.init_ui(default_conf)
            ui = uis.get_ui()
            ui.warning('Your configuration file has been updated.\n'
                       'Your old configuration has been moved to `{}`.'.format(color.dye_out(backup_path, 'filepath')))

        return True

    return False
