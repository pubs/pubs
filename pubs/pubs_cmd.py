# PYTHON_ARGCOMPLETE_OK

import sys
import collections
from . import uis
from . import p3
from . import config
from . import commands
from . import update
from . import plugins
from .__init__ import __version__
from .completion import autocomplete


CORE_CMDS = collections.OrderedDict([
    ('init', commands.init_cmd),
    ('conf', commands.conf_cmd),

    ('add', commands.add_cmd),
    ('rename', commands.rename_cmd),
    ('remove', commands.remove_cmd),
    ('list', commands.list_cmd),
    ('edit', commands.edit_cmd),
    ('tag', commands.tag_cmd),
    ('statistics', commands.statistics_cmd),

    ('doc', commands.doc_cmd),
    ('note', commands.note_cmd),

    ('export', commands.export_cmd),
    ('import', commands.import_cmd),

    ('websearch', commands.websearch_cmd),
    ('url', commands.url_cmd),
])


def execute(raw_args=sys.argv):

    try:
        conf_parser = p3.ArgumentParser(prog="pubs", add_help=False)
        conf_parser.add_argument("-c", "--config", help="path to config file",
                                 type=str, metavar="FILE")
        conf_parser.add_argument('--force-colors', dest='force_colors',
                                 action='store_true', default=False,
                                 help='color are not disabled when piping to a file or other commands')
        #conf_parser.add_argument("-u", "--update", help="update config if needed",
        #                         default=False, action='store_true')
        top_args, remaining_args = conf_parser.parse_known_args(raw_args[1:])

        if top_args.config:
            conf_path = top_args.config
        else:
            conf_path = config.get_confpath(verify=False)  # will be checked on load

        # Loading config
        try:
            conf = config.load_conf(path=conf_path)
            if update.update_check(conf, path=conf.filename):
                # an update happened, reload conf.
                conf = config.load_conf(path=conf_path)
        except config.ConfigurationNotFound:
            if len(remaining_args) == 0 or remaining_args[0] == 'init':
                conf = config.load_default_conf()
                conf.filename = conf_path
            else:
                raise

        uis.init_ui(conf, force_colors=top_args.force_colors)
        ui = uis.get_ui()

        desc = 'Pubs: your bibliography on the command line.\nVisit https://github.com/pubs/pubs for more information.'
        parser = p3.ArgumentParser(description=desc,
                                   prog="pubs", add_help=True)
        parser.add_argument('--version', action='version', version=__version__)
        subparsers = parser.add_subparsers(title="commands", dest="command")

        # Populate the parser with core commands
        for cmd_name, cmd_mod in CORE_CMDS.items():
            cmd_parser = cmd_mod.parser(subparsers, conf)
            cmd_parser.set_defaults(func=cmd_mod.command)

        # Extend with plugin commands
        plugins.load_plugins(conf, ui)
        for p in plugins.get_plugins().values():
            p.update_parser(subparsers, conf)

        # Eventually autocomplete
        autocomplete(parser)

        # Parse and run appropriate command
        # if no command, print help and exit peacefully (as '--help' does)
        args = parser.parse_args(remaining_args)
        if not args.command:
            parser.print_help(file=sys.stderr)
            sys.exit(2)

        args.prog = "pubs"  # FIXME?
        args.func(conf, args)

    except Exception as e:
        if not uis.get_ui().handle_exception(e):
            raise
