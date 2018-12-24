
import subprocess
from pipes import quote as shell_quote

from ...plugins import PapersPlugin


class GitPlugin(PapersPlugin):

    name = 'git'

    def __init__(self, conf):
        self.description = "Run git commands in the pubs directory"

    def update_parser(self, subparsers, conf):
        git_parser = self.parser(subparsers)
        git_parser.set_defaults(func=self.command)

    def parser(self, parser):
        self.parser = parser
        p = parser.add_parser(self.name, help=self.description)
        p.add_argument('arguments', nargs='*', help="look at man git")
        return p

    def command(self, conf, args):
        """Runs the git program in a shell"""
        subprocess.call(
            'pubs_git() {{\ngit -C {} $@\n}}\npubs_git {}'.format(
                conf['main']['pubsdir'],
                ' '.join([shell_quote(a) for a in args.arguments])
            ), shell=True)

