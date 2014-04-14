import subprocess

from .. import repo
from ..configs import config
from ..uis import get_ui
from .. import color
#from .helpers import add_references_argument, parse_reference


def parser(subparsers):
    parser = subparsers.add_parser('open',
            help='open the paper in a pdf viewer')
    parser.add_argument('-w', '--with', dest='with_command', default=None,
            help='command to use to open the document file')
    parser.add_argument('citekey',
            help='citekey of the paper')
    return parser


def command(args):

    ui = get_ui()
    with_command = args.with_command
    citekey = args.citekey

    rp = repo.Repository(config())
    paper = rp.pull_paper(citekey)
    if with_command is None:
        with_command = config().open_cmd

    if paper.docpath is None:
        ui.error('No document associated with the entry {}.'.format(
                 color.dye(citekey, color.citekey)))
        ui.exit()

    try:
        docpath = rp.databroker.real_docpath(paper.docpath)
        cmd = with_command.split()
        cmd.append(docpath)
        subprocess.Popen(cmd)
        ui.print_('{} opened.'.format(color.dye(docpath, color.filepath)))
    except OSError:
        ui.error("Command does not exist: %s." % with_command)
        ui.exit(127)
