import sys

import argparse
import collections

from . import uis
from . import configs
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


def _update_check(config, ui):
    if config.version_warning:
        code_version = __version__.split('.')
        repo_version = ('0.{}.0'.format(config.version)).split('.') # FIXME

        if repo_version > code_version:
            ui.warning(
                    'your repository was generated with an newer version'
                    ' of pubs (v{}) than the one you are using (v{}).'
                    '\n'.format(repo_version, code_version) +
                    'You should not use pubs until you install the '
                    'newest version. (use version_warning in you pubsrc '
                    'to bypass this error)')
            sys.exit()
        elif repo_version < code_version:
            ui.print_out(
                'warning: your repository version (v{})'.format(repo_version)
                + 'must   be updated to version {}.\n'.format(code_version)
                + "run 'pubs update'.")
            sys.exit()


def execute(raw_args=sys.argv):
    # loading config
    config = configs.Config()
    if len(raw_args) > 1 and raw_args[1] != 'init':
        try:
            config.load()
        except IOError as e:
            print('error: {}'.format(str(e)))
            sys.exit()
    config.as_global()

    uis.init_ui(config)
    ui = uis.get_ui()

    _update_check(config, ui)

    parser = argparse.ArgumentParser(description="research papers repository")
    subparsers = parser.add_subparsers(title="valid commands", dest="command")

    cmd_funcs = collections.OrderedDict()
    for cmd_name, cmd_mod in CORE_CMDS.items():
        cmd_mod.parser(subparsers)
        cmd_funcs[cmd_name] = cmd_mod.command

    # Extend with plugin commands
    plugins.load_plugins(ui, config.plugins.split())
    for p in plugins.get_plugins().values():
        cmd_funcs.update(p.get_commands(subparsers))

    args = parser.parse_args(raw_args[1:])
    args.prog = parser.prog  # Hack: there might be a better way...
    cmd = args.command
    del args.command

    cmd_funcs[cmd](args)
