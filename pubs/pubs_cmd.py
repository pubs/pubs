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
        if len(config.version) == 1: # support for deprecated version scheme.
            config.version = '0.{}.0'.format(config.version)
        repo_version = config.version.split('.')

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

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-c", "--config", help="path to config file",
                        type=str, metavar="FILE")
    args, remaining_args = conf_parser.parse_known_args(raw_args[1:])

    # loading config
    config = configs.Config()
    if remaining_args[0] != 'init':
        try:
            if args.config:
                config.load(args.config)
            else:
                config.load()
        except IOError as e:
            print('error: {}'.format(str(e)))
            sys.exit()
    config.as_global()

    uis.init_ui(config)
    ui = uis.get_ui()

    _update_check(config, ui)

    parser = argparse.ArgumentParser(parents=[conf_parser],
                                     description="research papers repository",
                                     prog="pubs", version=__version__, add_help=True)
    subparsers = parser.add_subparsers(title="valid commands", dest="command")
    cmd_funcs = collections.OrderedDict()
    for cmd_name, cmd_mod in CORE_CMDS.items():
        cmd_mod.parser(subparsers)
        cmd_funcs[cmd_name] = cmd_mod.command

    # Extend commands with plugin commands
    plugins.load_plugins(ui, config.plugins.split())
    for p in plugins.get_plugins().values():
        cmd_funcs.update(p.get_commands(subparsers))

    args = parser.parse_args(remaining_args)
    args.prog = parser.prog  # Hack: there might be a better way...
    cmd = args.command
    del args.command

    cmd_funcs[cmd](args)
