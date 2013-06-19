import subprocess

from .. import repo
from ..paper import NoDocumentFile
from .. import configs
from .. import color
from .helpers import add_references_argument, parse_reference


def parser(subparsers, config):
    parser = subparsers.add_parser('open',
            help='open the paper in a pdf viewer')
    parser.add_argument('-w', '--with', dest='with_command', default=None,
            help='command to use to open the document file')
    add_references_argument(parser, single=True)
    return parser


def command(config, ui, with_command, reference):
    rp = repo.Repository.from_directory(config)
    key = parse_reference(ui, rp, reference)
    paper = rp.get_paper(key)
    if with_command is None:
        with_command = config.get(configs.MAIN_SECTION, 'open-cmd')
    try:
        filepath = paper.get_document_path()
        subprocess.Popen([with_command, filepath])
        ui.print_('{} opened.'.format(color.dye(filepath, color.filepath)))
    except NoDocumentFile:
        ui.error('No document associated with the entry {}.'.format(
                 color.dye(key, color.citekey)))
        ui.exit()
    except OSError:
        ui.error("Command does not exist: %s." % with_command)
        ui.exit(127)
