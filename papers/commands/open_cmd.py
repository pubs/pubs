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
    papers = files.load_papers()
    try:
        filename = papers.get('papers', str(citekey))
    except configparser.NoOptionError:
        try:
            ck = papers.get('citekeys', 'ck'+str(citekey))
            filename = papers.get('papers', str(ck))
        except configparser.NoOptionError:
            print('{}error{}: paper with citekey or number {}{}{} not found{}'.format(
                color.red, color.grey, color.cyan, citekey, color.grey, color.end))
            exit(-1)
    meta_data = files.load_meta(filename)
    filepath = meta_data.get('metadata', 'path')
    p = subprocess.Popen(['open', filepath])
    print('{}{}{} opened.{}'.format(color.cyan, filepath, color.grey, color.end))