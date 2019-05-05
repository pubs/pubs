import shlex
import subprocess
from pipes import quote as shell_quote

from ...plugins import PapersPlugin
from ...pubs_cmd import execute


class Alias(object):

    def __init__(self, name, definition, description=None):
        self.name = name
        self.definition = definition
        if not description:
            self.description = "user alias for `%s`" % definition
        else:
            self.description = description

    def parser(self, parser):
        self.parser = parser
        p = parser.add_parser(self.name, help=self.description)
        p.add_argument('arguments', nargs='*',
                       help="arguments to be passed to %s" % self.name)
        return p

    def command(self, conf, args):
        raise NotImplementedError

    @classmethod
    def create_alias(cls, name, definition, description=None):
        if len(definition) > 0 and definition[0] == '!':
            return ShellAlias(name, definition[1:], description)
        else:
            return CommandAlias(name, definition, description)


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
            'pubs_alias_fun () {{\n{}\n}}\npubs_alias_fun {}'.format(
                self.definition,
                ' '.join([shell_quote(a) for a in args.arguments])
            ), shell=True)


class AliasPlugin(PapersPlugin):

    name = 'alias'

    def __init__(self, conf, ui):
        self.aliases = []
        if 'alias' in conf['plugins']:
            for name, entry in conf['plugins']['alias'].items():
                if isinstance(entry, dict):
                    definition = entry.get('command')
                    description = entry.get('description', None)
                else:
                    definition = entry
                    description = None

                alias = Alias.create_alias(name, definition, description)
                self.aliases.append(alias)

    def update_parser(self, subparsers, conf):
        """Add subcommand to the provided subparser"""
        for alias in self.aliases:
            alias_parser = alias.parser(subparsers)
            alias_parser.set_defaults(func=alias.command)
