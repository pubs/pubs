import subprocess

from .. import color
from .. import repo

def parser(subparsers, config):
    parser = subparsers.add_parser('open', help='{}open the paper in a pdf viewer{}'.format(color.normal, color.end))
    parser.add_argument('citekey', help='{}the paper associated citekey{}'.format(color.normal, color.end))
    return parser

def command(config, citekey):
    rp = repo.Repository()
    paper = rp.paper_from_any(citekey, fatal = True)
    filepath = paper.metadata.get('metadata', 'path')

    p = subprocess.Popen(['open', filepath])
    print('{}{}{} opened.{}'.format(color.filepath, filepath, color.normal, color.end))