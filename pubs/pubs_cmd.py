import sys

import argparse
import collections

from . import uis
from . import config
from . import commands
from . import plugins
from .__init__ import __version__


CORE_CMDS = collections.OrderedDict([
        ('init',        commands.init_cmd),
        ('add',         commands.add_cmd),
        ('rename',      commands.rename_cmd),
        ('remove',      commands.remove_cmd),
        ('list',        commands.list_cmd),

        ('attach',      commands.attach_cmd),
        ('open',        commands.open_cmd),
        ('tag',         commands.tag_cmd),
        ('note',        commands.note_cmd),

        ('export',      commands.export_cmd),
        ('import',      commands.import_cmd),

        ('websearch',   commands.websearch_cmd),
        ('edit',        commands.edit_cmd),
        # ('update',      commands.update_cmd),
        ])


def _update_check(conf, ui):
    code_version = __version__.split('.')
    if len(conf['internal']['version']) == 1: # support for deprecated version scheme.
        conf['internal']['version'] = '0.{}.0'.format(conf['internal']['version'])
    repo_version = conf['internal']['version'].split('.')

    if repo_version > code_version:
        ui.warning(
                'your repository was generated with an newer version'
                ' of pubs (v{}) than the one you are using (v{}).'
                '\n'.format(repo_version, code_version) +
                'You should not use pubs until you install the '
                'newest version.')
        sys.exit()
    elif repo_version < code_version:
        ui.message(
            'warning: your repository version (v{})'.format(repo_version)
            + 'must   be updated to version {}.\n'.format(code_version)
            + "run 'pubs update'.")
        sys.exit()


def execute(raw_args=sys.argv):
    # loading config
    if len(raw_args) > 1 and raw_args[1] != 'init':
        try:
            conf = config.load_conf(check_conf=True)
        except IOError as e:
            print('error: {}'.format(str(e)))
            sys.exit()
    else:
        conf = config.load_default_conf()

    uis.init_ui(conf)
    ui = uis.get_ui()

    _update_check(conf, ui)

    parser = argparse.ArgumentParser(description="research papers repository")
    subparsers = parser.add_subparsers(title="valid commands", dest="command")

    cmd_funcs = collections.OrderedDict()
    for cmd_name, cmd_mod in CORE_CMDS.items():
        cmd_mod.parser(subparsers)
        cmd_funcs[cmd_name] = cmd_mod.command

    # Extend with plugin commands
    plugins.load_plugins(ui, conf['plugins']['active'])
    for p in plugins.get_plugins().values():
        cmd_funcs.update(p.get_commands(subparsers))

    args = parser.parse_args(raw_args[1:])
    args.prog = parser.prog  # Hack: there might be a better way...
    cmd = args.command
    del args.command

    cmd_funcs[cmd](conf, args)
