import sys
import argparse
import collections
from . import uis
from . import config
from . import commands
from . import update
from . import plugins
from .__init__ import __version__

CORE_CMDS = collections.OrderedDict([
    ('init', commands.init_cmd),
    ('conf', commands.conf_cmd),

    ('add', commands.add_cmd),
    ('rename', commands.rename_cmd),
    ('remove', commands.remove_cmd),
    ('list', commands.list_cmd),

    ('attach', commands.attach_cmd),
    ('open', commands.open_cmd),
    ('tag', commands.tag_cmd),
    ('note', commands.note_cmd),

    ('export', commands.export_cmd),
    ('import', commands.import_cmd),

    ('websearch', commands.websearch_cmd),
    ('edit', commands.edit_cmd),
])


def execute(raw_args=sys.argv):

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-c", "--config", help="path to config file",
                             type=str, metavar="FILE")
    args, remaining_args = conf_parser.parse_known_args(raw_args[1:])

    if args.config:
        conf_path = args.config
    else:
        conf_path = config.get_confpath(verify=False)  # will be checked on load

    # Loading config
    if len(remaining_args) > 0 and remaining_args[0] != 'init':
        try:
            conf = config.load_conf(path=conf_path, check=False)
            if update.update_check(conf, path=conf.filename):  # an update happened, reload conf.
                conf = config.load_conf(path=conf_path, check=False)
            config.check_conf(conf)
        except IOError as e:
            print('error: {}'.format(str(e)))
            sys.exit()
    else:
        conf = config.load_default_conf()
        conf.filename = conf_path

    uis.init_ui(conf)
    ui = uis.get_ui()

    parser = argparse.ArgumentParser(description="research papers repository",
                                     prog="pubs", add_help=True)
    parser.add_argument('--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(title="valid commands", dest="command")
    subparsers.required = True

    # Populate the parser with core commands
    for cmd_name, cmd_mod in CORE_CMDS.items():
        cmd_parser = cmd_mod.parser(subparsers)
        cmd_parser.set_defaults(func=cmd_mod.command)

    # Extend with plugin commands
    plugins.load_plugins(conf, ui)
    for p in plugins.get_plugins().values():
        p.update_parser(subparsers)

    # Parse and run appropriate command
    args = parser.parse_args(remaining_args)
    args.func(conf, args)
