import subprocess

from .. import repo
from ..configs import config
from ..uis import get_ui
from .. import color
from ..content import system_path
from ..utils import resolve_citekey

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

    rp = repo.Repository(config())
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    paper = rp.pull_paper(citekey)

    if with_command is None:
        with_command = config().open_cmd

    if paper.docpath is None:
        ui.error('No document associated with the entry {}.'.format(
                 color.dye_err(citekey, color.citekey)))
        ui.exit()

    try:
        docpath = system_path(rp.databroker.real_docpath(paper.docpath))
        cmd = with_command.split()
        cmd.append(docpath)
        subprocess.Popen(cmd)
        ui.print_out('{} opened.'.format(color.dye(docpath, color.filepath)))
    except OSError:
        ui.error("Command does not exist: %s." % with_command)
        ui.exit(127)
