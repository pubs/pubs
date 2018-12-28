
import subprocess
from pipes import quote as shell_quote

from ...plugins import PapersPlugin
from ...events import RemoveEvent, RenameEvent, AddEvent


class GitPlugin(PapersPlugin):

    name = 'git'
    pubsdir = None

    def __init__(self, conf):
        self.description = "Run git commands in the pubs directory"
        # Needed for the event listening
        GitPlugin.pubsdir = conf['main']['pubsdir']

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
        for a in args.arguments:
            print(a)
        GitPlugin.shell(' '.join([shell_quote(a) for a in args.arguments]))

    @classmethod
    def shell(cls, cmd):
        subprocess.call('git -C {} {}'.format(cls.pubsdir, cmd), shell=True)


@RenameEvent.listen()
def git_rename(RenameEventInstance):
    new_key = RenameEventInstance.paper.citekey
    old_key = RenameEventInstance.old_citekey

    # Stage the changes and commit
    GitPlugin.shell("add \*/{}.\*".format(old_key))
    GitPlugin.shell("add \*/{}.\*".format(new_key))
    GitPlugin.shell('commit -m "Renamed {} to {}"'.format(old_key, new_key)


@RemoveEvent.listen()
def git_remove(RemoveEventInstance):
    citekey = RemoveEventInstance.old_citekey

    # Stage the changes and commit
    GitPlugin.shell("add \*/{}.\*".format(citekey))
    GitPlugin.shell('commit -m "Removed {}"'.format(citekey))


@AddEvent.listen()
def git_add(AddEventInstance):
    citekey = AddEventInstance.citekey

    # Stage the changes and commit
    GitPlugin.shell("add \*/{}.\*".format(citekey))
    GitPlugin.shell('commit -m "Added {}"'.format(citekey))

