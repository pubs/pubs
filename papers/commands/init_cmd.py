# init command

import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from .. import color
from .. import files

def parser(subparsers, config):
    parser = subparsers.add_parser('init', help="initialize the .papers directory")
    return parser

def command(config):
    """Create a .papers directory"""
    # create dir
    papersdir = os.getcwd() + '/.papers'

    if not os.path.exists(papersdir):
        print('{}initializing papers in {}{}{}'.format(
               color.grey, color.cyan, papersdir, color.end))
        
        os.makedirs(os.path.join(papersdir, 'bibdata'))
        os.makedirs(os.path.join(papersdir, 'meta'))
        
        papers = {}
        papers['citekeys'] = []
        files.save_papers(papers)

    else:
        print('{}error {} : papers already present in {}{}{}'.format(
               color.red, color.grey, color.cyan, papersdir, color.end))
        exit(-1)
