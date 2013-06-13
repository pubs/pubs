import subprocess

from .. import repo
from ..paper import NoDocumentFile
from .. import configs


def parser(subparsers, config):
    parser = subparsers.add_parser('open',
            help='open the paper in a pdf viewer')
    parser.add_argument('citekey',
            help='the paper associated citekey')
    return parser


def command(config, ui, citekey):
    rp = repo.Repository.from_directory(config)
    paper = rp.paper_from_ref(citekey, fatal=True)
    try:
        filepath = paper.get_document_path()
        subprocess.Popen([config.get(configs.MAIN_SECTION, 'open-cmd'),
                          filepath])
        print('{} opened.'.format(color.dye(filepath, color.filepath)))
    except NoDocumentFile:
        ui.error('No document associated with the entry {}.'.format(
                 color.dye(citekey, color.citekey)))
        ui.exit()
