
import subprocess
from pipes import quote as shell_quote

from ...plugins import PapersPlugin
from ...events import *


class GitPlugin(PapersPlugin):

    name = 'git'
    description = "Run git commands in the pubs directory"

    def __init__(self, conf):
        self.pubsdir = conf['main']['pubsdir']

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
    git = GitPlugin.get_instance()
    git.shell("add \*/{}.\*".format(old_key))
    git.shell("add \*/{}.\*".format(new_key))
    git.shell('commit -m "Renamed citekey {} to {}"'.format(old_key, new_key))


@RemoveEvent.listen()
def git_remove(RemoveEventInstance):
    citekey = RemoveEventInstance.citekey

    # Stage the changes and commit
    git = GitPlugin.get_instance()
    git.shell("add \*/{}.\*".format(citekey))
    git.shell('commit -m "Removed files for {}"'.format(citekey))


@AddEvent.listen()
def git_add(AddEventInstance):
    citekey = AddEventInstance.citekey

    # Stage the changes and commit
    git = GitPlugin.get_instance()
    git.shell("add \*/{}.\*".format(citekey))
    git.shell('commit -m "Added files for {}"'.format(citekey))


@EditEvent.listen()
def git_edit(EditEventInstance):
    pass


@TagEvent.listen()
def git_tag(TagEventInstance):
    pass


@DocEvent.listen()
def git_doc(DocEventInstance):
    citekey = DocEventInstance.citekey

    # Stage the changes and commit
    git = GitPlugin.get_instance()
    git.shell("add \*/{}.\*".format(citekey))
    if DocEventInstance.action == 'add':
        git.shell('commit -m "Added document for {}"'.format(citekey))
    elif DocEventInstance.action == 'remove':
        git.shell('commit -m "Removed document for {}"'.format(citekey))


@NoteEvent.listen()
def git_note(NoteEventInstance):
    pass

