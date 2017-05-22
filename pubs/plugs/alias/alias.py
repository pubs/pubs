import subprocess
import shlex

from ...plugins import PapersPlugin
from ...pubs_cmd import execute


class Alias(object):

    def __init__(self, name, definition):
        self.name = name
        self.definition = definition

    def parser(self, parser):
        self.parser = parser
        p = parser.add_parser(self.name, help='user defined command')
        p.add_argument('arguments', nargs='*',
            help="arguments to be passed to the user defined command")
        return p

    def command(self, conf, args):
        raise NotImplementedError

    @classmethod
    def create_alias(cls, name, definition):
        if len(definition) > 0 and definition[0] == '!':
            return ShellAlias(name, definition[1:])
        else:
            return CommandAlias(name, definition)


class CommandAlias(Alias):
    """Default kind of alias.
    - definition is used as a papers command
    - other arguments are passed to the command
    """

    def command(self, conf, args):
        raw_args = ([args.prog]
                    + shlex.split(self.definition
                    + ' '
                    + ' '.join(args.arguments)))
        execute(raw_args)


class ShellAlias(Alias):

    def command(self, conf, args):
        """Uses a shell function so that arguments can be used in the command
        as shell arguments.
        """
        subprocess.call(
                'papers_alias_fun () {{\n{}\n}}\npapers_alias_fun {}'.format(
                    self.definition, ' '.join(args.arguments)),
                shell=True)


class AliasPlugin(PapersPlugin):

    name = 'alias'

    def __init__(self, conf):
        self.aliases = []
        if 'alias' in conf['plugins']:
            for name, definition in conf['plugins']['alias'].items():
                self.aliases.append(Alias.create_alias(name, definition))

    def update_parser(self, subparsers, conf):
        """Add subcommand to the provided subparser"""
        for alias in self.aliases:
            alias_parser = alias.parser(subparsers)
            alias_parser.set_defaults(func=alias.command)
