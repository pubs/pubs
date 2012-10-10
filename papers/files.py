
import sys, os
import subprocess
import tempfile

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
    
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
    print '{}error{}: you need to install Pybtex; try running \'pip install pybtex\' or \'easy_install pybtex\''.format(color.red, color.end)


_papersdir = None

def find_papersdir():
    """Find .papers directory in this directory and the parent directories"""
    global _papersdir
    if _papersdir is None:
        curdir = os.path.abspath(os.getcwd())
        while curdir != '':
            if os.path.exists(curdir + '/.papers') and os.path.isdir(curdir + '/.papers'):
                _papersdir = curdir + '/.papers'
                curdir = ''
            if curdir == '/':
                curdir = ''
            else:
                curdir = os.path.split(curdir)[0]

        if _papersdir is None:
            print '{}error{} : no papers repo found in this directory or in any parent directory.{}'.format(
                   color.red, color.grey, color.end)
            exit(-1)

    return _papersdir


def check_file(filepath):
    if not os.path.exists(filepath):
        print '{}error{}: {}{}{} does not exists{}'.format(
               color.red, color.grey, color.cyan, filepath, color.grey, color.end)
        exit(-1)
    if not os.path.isfile(filepath):
        print '{}error{}: {}{}{} is not a file{}'.format(
               color.red, color.grey, color.cyan, filepath, color.grey, color.end)
        exit(-1)

def write_configfile(config, filepath):
    try:
        with open(filepath, 'w') as f:
            config.write(f)
    except IOError as e:
        print '{}error{} : impossible to write on file {}{:s}{}'.format(
               color.red, color.grey, color.cyan, filepath, color.end)
        print 'Verify permissions'
        exit(-1)

def read_configfile(filepath):
    try:
        with open(filepath, 'r') as f:
            config = configparser.ConfigParser()
            config.readfp(f)
            return config
    except IOError as e:
        print '{}error{} : impossible to read file {}{:s}{}'.format(
               color.red, color.grey, color.cyan, filepath, color.end)
        print 'Verify permissions'
        exit(-1)

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


def write_papers(config):
    write_configfile(config, find_papersdir() + os.sep + 'papers')

def load_papers():
    return read_configfile(find_papersdir() + os.sep + 'papers')

def load_bibdata(filename):
    fullbibpath = find_papersdir() + os.sep + 'bibdata' + os.sep + filename + '.bibyaml'
    return load_externalbibfile(fullbibpath)

def write_bibdata(bib_data, filename):
    filepath = find_papersdir() + os.sep + 'bibdata' + os.sep + filename + '.bibyaml'
    with open(filepath, 'w') as f:
        parser = pybtex.database.output.bibyaml.Writer()
        parser.write_stream(bib_data, f)

def write_meta(meta_data, filename):
    filepath = find_papersdir() + os.sep + 'meta' + os.sep + filename + '.meta'
    write_configfile(meta_data, filepath)

def load_meta(filename):
    filepath = find_papersdir() + os.sep + 'meta' + os.sep + filename + '.meta'
    return read_configfile(filepath)


try:
    EDITOR = os.environ['EDITOR']
except KeyError:
    EDITOR = 'nano'

def vim_input(initial = ""):
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
