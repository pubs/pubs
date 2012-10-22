import subprocess

from .. import color
from .. import repo
from ..paper import NoDocumentFile

def parser(subparsers, config):
    parser = subparsers.add_parser('open', help='{}open the paper in a pdf viewer{}'.format(color.normal, color.end))
    parser.add_argument('citekey', help='{}the paper associated citekey{}'.format(color.normal, color.end))
    return parser

def command(config, citekey):
    rp = repo.Repository()
    paper = rp.paper_from_any(citekey, fatal = True)
    try:
        if paper.check_file():
            filepath = paper.get_file_path()

            p = subprocess.Popen(['open', filepath])
            print('{}{}{} opened.{}'.format(
                color.filepath, filepath, color.normal, color.end))
    except NoDocumentFile:
        print('{}error{}: No document associated to this entry {}{}{}'.format(
            color.error, color.normal, color.citekey, citekey, color.end))
        exit(-1)

