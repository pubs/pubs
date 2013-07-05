#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import sys

import argparse
import collections

from .ui import UI
from . import configs
from . import commands
from . import plugins
from .__init__ import __version__

cmds = collections.OrderedDict([
        ('init',        commands.init_cmd),
        ('add',         commands.add_cmd),
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

def _update_check(config, ui):
    if config.version_warning:
        code_version = int(__version__)
        repo_version = int(config.version)

        if repo_version > code_version:
            ui.print_('warning: your repository was generated with an newer version'
                      ' of papers (v{}) than the one you are using (v{}).\n'.format(
                       repo_version, code_version) +
                      '         you should not use papers until you install the '
                      'newest version. (use version_warning in you papersrc '
                      'to bypass this error)')
            sys.exit()
        elif repo_version < code_version:
            ui.print_(
                'warning: your repository version (v{})'.format(repo_version)
                + 'must be updated to version {}.\n'.format(code_version)
                + "run 'papers update'.")
            sys.exit()


def execute(raw_args = sys.argv):
    # loading config
    config = configs.Config()
    config.load()
    config.as_global()

    ui = UI(config)

    _update_check(config, ui)

    # Extend with plugin commands
    plugins.load_plugins(ui, config.plugins.split())
    for p in plugins.get_plugins().values():
        if getattr(p, 'parser') and getattr(p, 'command'):
            cmds.update(collections.OrderedDict([(p.name, p)]))

    parser = argparse.ArgumentParser(description="research papers repository")
    subparsers = parser.add_subparsers(title="valid commands", dest="command")

    for cmd_mod in cmds.values():
        subparser = cmd_mod.parser(subparsers)  # why do we return the subparser ?

    args = parser.parse_args(raw_args[1:])

    args.ui = ui
    cmd = args.command
    del args.command

    cmds[cmd].command(args)
