import subprocess

from .. import repo
from ..paper import NoDocumentFile
from ..configs import config
from ..uis import get_ui
from .. import color
from .helpers import add_references_argument, parse_reference


def parser(subparsers):
    parser = subparsers.add_parser('open',
            help='open the paper in a pdf viewer')
    parser.add_argument('-w', '--with', dest='with_command', default=None,
            help='command to use to open the document file')
    add_references_argument(parser, single=True)
    return parser


def command(args):

    ui = get_ui()
    with_command = args.with_command
    reference = args.reference

    rp = repo.Repository(config())
    key = parse_reference(ui, rp, reference)
    paper = rp.get_paper(key)
    if with_command is None:
        with_command = config().open_cmd
    try:
        filepath = paper.get_document_path()
        cmd = with_command.split()
        cmd.append(filepath)
        subprocess.Popen(cmd)
        ui.print_('{} opened.'.format(color.dye(filepath, color.filepath)))
    except NoDocumentFile:
        ui.error('No document associated with the entry {}.'.format(
                 color.dye(key, color.citekey)))
        ui.exit()
    except OSError:
        ui.error("Command does not exist: %s." % with_command)
        ui.exit(127)
