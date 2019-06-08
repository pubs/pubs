import os
import sys
import argparse
from subprocess import Popen, PIPE, STDOUT
from pipes import quote as shell_quote

from ... import uis
from ...plugins import PapersPlugin
from ...events import PaperChangeEvent, PostCommandEvent


GITIGNORE = """# files or directories for the git plugin to ignore
.gitignore
.cache/
"""


class GitPlugin(PapersPlugin):
    """The git plugin creates a git repository in the pubs directory and commit the changes
    to the pubs repository everytime a paper is modified.

    It also add the `pubs git` subcommand, so git commands can be executed in the git repository
    from the command line.
    """

    name = 'git'
    description = "Run git commands in the pubs directory"

    def __init__(self, conf, ui):
        self.ui = ui
        self.pubsdir     = os.path.expanduser(conf['main']['pubsdir'])
        self.manual      = conf['plugins'].get('git', {}).get('manual', False)
        self.force_color = conf['plugins'].get('git', {}).get('force_color', True)
        self.quiet   = conf['plugins'].get('git', {}).get('quiet', True)
        self.list_of_changes = []
        self._gitinit()

    def _gitinit(self):
        """Initialize the git repository if necessary."""
        # check that a `.git` directory is present in the pubs dir
        git_path = os.path.join(self.pubsdir, '.git')
        if not os.path.isdir(git_path):
            try:
                self.shell('init')
            except RuntimeError as exc:
                self.ui.error(exc.args[0])
                sys.exit(1)
        # check that a `.gitignore` file is present
        gitignore_path = os.path.join(self.pubsdir, '.gitignore')
        if not os.path.isfile(gitignore_path):
            with open(gitignore_path, 'w') as fd:
                fd.write(GITIGNORE)

    def update_parser(self, subparsers, conf):
        """Allow the usage of the pubs git subcommand"""
        git_parser = subparsers.add_parser(self.name, help=self.description)
        # FIXME: there may be some problems here with the -c argument being ambiguous between
        # pubs and git.
        git_parser.add_argument('arguments', nargs=argparse.REMAINDER, help="look at man git")
        git_parser.set_defaults(func=self.command)

    def command(self, conf, args):
        """Execute a git command in the pubs directory"""
        self.shell(' '.join([shell_quote(a) for a in args.arguments]), command=True)

    def shell(self, cmd, input_stdin=None, command=False):
        """Runs the git program in a shell

        :param cmd: the git command, and all arguments, as a single string (e.g. 'add .')
        :param input_stdin:  if Python 3, must be bytes (i.e., from str, s.encode('utf-8'))
        :param command: if True, we're dealing with an explicit `pubs git` invocation.
        """
        colorize = ' -c color.ui=always' if self.force_color else ''
        git_cmd = 'git -C {}{} {}'.format(self.pubsdir, colorize, cmd)
        #print(git_cmd)
        p = Popen(git_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
        output, err = p.communicate(input_stdin)
        p.wait()

        if p.returncode != 0:
            raise RuntimeError('The git plugin encountered an error when running the git command:\n' +
                '{}\n\nReturned output:\n{}\n'.format(git_cmd, output.decode('utf-8')) +
                'If needed, you may fix the state of the {} git repository '.format(self.pubsdir) +
                'manually.\nIf relevant, you may submit a bug report at ' +
                'https://github.com/pubs/pubs/issues')
        elif command:
            self.ui.message(output.decode('utf-8'), end='')
        elif not self.quiet:
            self.ui.info(output.decode('utf-8'))
        return output, err, p.returncode


@PaperChangeEvent.listen()
def paper_change_event(event):
    """When a paper is changed, commit the changes to the directory."""
    if GitPlugin.is_loaded():
        git = GitPlugin.get_instance()
        if not git.manual:
            event_desc = event.description
            for a, b in [('\\','\\\\'), ('"','\\"'), ('$','\\$'), ('`','\\`')]:
                event_desc = event_desc.replace(a, b)
            git.list_of_changes.append(event_desc)

@PostCommandEvent.listen()
def git_commit(event):
    if GitPlugin.is_loaded():
        try:
            git = GitPlugin.get_instance()
            if len(git.list_of_changes) > 0:
                if not git.manual:
                    title = ' '.join(sys.argv) + '\n'
                    message = '\n'.join([title] + git.list_of_changes)

                    git.shell('add .')
                    git.shell('commit -F-', message.encode('utf-8'))
        except RuntimeError as exc:
            uis.get_ui().warning(exc.args[0])
