import sys

import argparse
import collections

from . import uis
from . import config
from . import commands
from . import update
from . import plugins


CORE_CMDS = collections.OrderedDict([
        ('init',        commands.init_cmd),
        ('conf',        commands.conf_cmd),

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
        ])


def execute(raw_args=sys.argv):
    # loading config
    if len(raw_args) > 1 and raw_args[1] != 'init':
        try:
            conf = config.load_conf(check=False)
            if update.update_check(conf): # an update happened, reload conf.
                conf = config.load_conf(check=False)
            config.check_conf(conf)
        except IOError as e:
            print('error: {}'.format(str(e)))
            sys.exit()
    else:
        conf = config.load_default_conf()

    uis.init_ui(conf)
    ui = uis.get_ui()

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
