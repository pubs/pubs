try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import subprocess

from .. import files
from .. import color

def parser(subparsers, config):
    parser = subparsers.add_parser('open', help="open the paper in a pdf viewer")
    parser.add_argument("citekey", help="the paper associated citekey")
    return parser

def command(config, citekey):
    papers = files.read_papers()
    try:
        filename = papers.get('papers', 'p' + str(citekey))
    except configparser.NoOptionError:
        print('{}error{}: paper with citekey {}{}{} not found{}'.format(
                color.red, color.grey, color.cyan, citekey, color.grey, color.end))
        exit(-1)
    meta_data = files.load_meta(filename)
    filepath = meta_data.get('metadata', 'path')
    p = subprocess.Popen(['open', filepath])
    print('{}{}{} opened.{}'.format(color.cyan, filepath, color.grey, color.end))