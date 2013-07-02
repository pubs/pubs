#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import sys

import argparse
import collections

from .ui import UI
from . import configs
from . import commands
from . import plugin

cmds = collections.OrderedDict([
        ('init',        commands.init_cmd),
        ('add',         commands.add_cmd),
        ('add_library', commands.add_library_cmd),
        ('import',      commands.import_cmd),
        ('export',      commands.export_cmd),
        ('list',        commands.list_cmd),
        ('edit',        commands.edit_cmd),
        ('remove',      commands.remove_cmd),
        ('open',        commands.open_cmd),
        ('websearch',   commands.websearch_cmd),
        ('tag',         commands.tag_cmd),
        ('attach',      commands.attach_cmd),
        ('update',      commands.update_cmd),
        ])


def execute(raw_args = sys.argv):
    # loading config
    config = configs.Config()
    config.load()
    config.as_global()

    ui = UI(config)

    # Extend with plugin commands
    plugin.load_plugins(ui, config.plugins.split())
    for p in plugin.get_plugins().values():
        cmds.update(collections.OrderedDict([(p.name, p)]))

    parser = argparse.ArgumentParser(description="research papers repository")
    subparsers = parser.add_subparsers(title="valid commands", dest="command")

    for cmd_mod in cmds.values():
        subparser = cmd_mod.parser(subparsers)  # why do we return the subparser ?

    args = parser.parse_args(raw_args[1:])

    args.ui = ui
    cmd = args.command
    del args.command

    cmds[cmd].command(**vars(args))
