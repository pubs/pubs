import subprocess

from ..color import colored
from .. import repo
from ..paper import NoDocumentFile
from . import configs


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
        subprocess.Popen([config.get(configs.MAIN_SECTION, 'open-cmd'), filepath])
        print("%s opened." % colored(filepath, 'filepath'))
    except NoDocumentFile:
        print("%s: No document associated to this entry %s."
                % (colored('error', 'error'), colored(citekey, 'citekey')))
        exit(-1)
