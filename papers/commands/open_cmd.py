import subprocess

from .. import repo
from ..paper import NoDocumentFile
from .. import configs


def parser(subparsers, config):
    parser = subparsers.add_parser('open',
            help='open the paper in a pdf viewer')
    parser.add_argument('-w', '--with', dest='with_command', default=None,
            help='command to use to open the document file')
    parser.add_argument('citekey',
            help='the paper associated citekey')
    return parser


def command(config, ui, with_command, citekey):
    rp = repo.Repository.from_directory(config)
    paper = rp.paper_from_ref(citekey, fatal=True)
    if with_command is None:
        with_command = config.get(configs.MAIN_SECTION, 'open-cmd')
    try:
        filepath = paper.get_document_path()
        subprocess.Popen([with_command, filepath])
        ui.print_("%s opened." % ui.colored(filepath, 'filepath'))
    except NoDocumentFile:
        ui.error("No document associated with the entry %s."
                 % ui.colored(citekey, 'citekey'))
        ui.exit()
    except OSError:
        ui.error("Command does not exist: %s." % with_command)
        ui.exit(127)
