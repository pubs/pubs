import os
import subprocess
import tempfile

import yaml

import color

try:
    import pybtex
    import pybtex.database
    import pybtex.database.input
    import pybtex.database.input.bibtex
    import pybtex.database.input.bibtexml
    import pybtex.database.input.bibyaml
    import pybtex.database.output
    import pybtex.database.output.bibtex
    import pybtex.database.output.bibtexml
    import pybtex.database.output.bibyaml

except ImportError:
    print '{}error{}: you need to install Pybtex; try running \'pip install'
    'pybtex\' or \'easy_install pybtex\''.format(color.red, color.end)


_papersdir = None

try:
    EDITOR = os.environ['EDITOR']
except KeyError:
    EDITOR = 'nano'


def find_papersdir():
    """Find .papers directory in this directory and the parent directories"""
    global _papersdir
    if _papersdir is None:
        curdir = os.path.abspath(os.getcwd())
        while curdir != '':
            if (os.path.exists(curdir + '/.papers')
                    and os.path.isdir(curdir + '/.papers')):
                _papersdir = curdir + '/.papers'
                curdir = ''
            if curdir == '/':
                curdir = ''
            else:
                curdir = os.path.split(curdir)[0]
        if _papersdir is None:
            print '{}error{} : no papers repo found in this directory or in'
            'any parent directory.{}'.format(color.red, color.grey, color.end)
            exit(-1)
    return _papersdir


def name_from_path(fullpdfpath, verbose=False):
    name, ext = os.path.splitext(os.path.split(fullpdfpath)[1])
    if verbose:
        if ext != '.pdf' and ext != '.ps':
            print('{}warning{}: extension {}{}{} not recognized{}'.format(
                   color.yellow, color.grey, color.cyan, ext, color.grey,
                   color.end))
    return name, ext


def check_file(filepath):
    if not os.path.exists(filepath):
        print '{}error{}: {}{}{} does not exists{}'.format(
               color.red, color.grey, color.cyan, filepath, color.grey,
               color.end)
        exit(-1)
    if not os.path.isfile(filepath):
        print '{}error{}: {}{}{} is not a file{}'.format(
               color.red, color.grey, color.cyan, filepath, color.grey,
               color.end)
        exit(-1)


# yaml I/O

def write_yamlfile(filepath, datamap):
    try:
        with open(filepath, 'w') as f:
            yaml.dump(datamap, f)
    except IOError:
        print '{}error{} : impossible to read file {}{:s}{}'.format(
               color.red, color.grey, color.cyan, filepath, color.end)
        exit(-1)


def read_yamlfile(filepath):
    check_file(filepath)
    try:
        with open(filepath, 'r') as f:
            return yaml.load(f)
    except IOError:
        print '{}error{} : impossible to read file {}{:s}{}'.format(
               color.red, color.grey, color.cyan, filepath, color.end)
        exit(-1)


def load_bibdata(filename, filepath):
    return load_externalbibfile(filepath)


def save_bibdata(bib_data, filepath):
    with open(filepath, 'w') as f:
        parser = pybtex.database.output.bibyaml.Writer()
        parser.write_stream(bib_data, f)


def save_meta(meta_data, filepath):
    write_yamlfile(filepath, meta_data)


def load_meta(filepath):
    return read_yamlfile(filepath)


# specific to bibliography data

def load_externalbibfile(fullbibpath):
    check_file(fullbibpath)

    filename, ext = os.path.splitext(os.path.split(fullbibpath)[1])
    if ext == '.bib':
        parser = pybtex.database.input.bibtex.Parser()
        bib_data = parser.parse_file(fullbibpath)
    elif ext == '.xml' or ext == '.bibtexml':
        parser = pybtex.database.input.bibtexml.Parser()
        bib_data = parser.parse_file(fullbibpath)
    elif ext == '.yaml' or ext == '.bibyaml':
        parser = pybtex.database.input.bibyaml.Parser()
        bib_data = parser.parse_file(fullbibpath)
    else:
        print '{}error{}: {}{}{} not recognized format for bibliography{}'.format(
               color.red, color.grey, color.cyan, ext, color.grey, color.end)
        exit(-1)

    return bib_data


# vim input

def vim_input(initial=""):
    """Use an editor to get input"""

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as temp_file:
        tfile_name = temp_file.name
        temp_file.write(initial)
        temp_file.flush()
        subprocess.call([EDITOR, tfile_name])

    with open(tfile_name) as temp_file:
        content = temp_file.read()
        os.remove(tfile_name)

    return content
