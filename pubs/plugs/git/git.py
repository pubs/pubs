
import subprocess
from pipes import quote as shell_quote

from ...plugins import PapersPlugin
from ...events import PaperEvent, RenameEvent


class GitPlugin(PapersPlugin):

    name = 'git'
    description = "Run git commands in the pubs directory"

    def __init__(self, conf):
        self.pubsdir = conf['main']['pubsdir']

    def update_parser(self, subparsers, conf):
        git_parser = subparsers.add_parser(self.name, help=self.description)
        git_parser.add_argument('arguments', nargs='*', help="look at man git")
        git_parser.set_defaults(func=self.command)

    def command(self, conf, args):
        """Runs the git program in a shell"""
        self.shell(' '.join([shell_quote(a) for a in args.arguments]))

    def shell(self, cmd):
        subprocess.call('git -C {} {}'.format(self.pubsdir, cmd), shell=True)


@PaperEvent.listen()
def git_commit_event(PaperEventInstance):
    # Stage the changes and commit
    git = GitPlugin.get_instance()
    if isinstance(PaperEventInstance, RenameEvent):
        git.shell("add \*/{}.\*".format(PaperEventInstance.old_citekey))
    git.shell("add \*/{}.\*".format(PaperEventInstance.citekey))
    cmesg = PaperEventInstance.description
    cmesg = cmesg.replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('`','\\`')
    git.shell('commit -m "{}"'.format(cmesg))
