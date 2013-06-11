import os
import subprocess
import tempfile

import yaml

from .color import colored
from . import configs

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
    print(colored('error', 'error')
            + ': you need to install Pybtex; try running \'pip install'
            'pybtex\' or \'easy_install pybtex\'')


_papersdir = None

BIB_EXTENSIONS = ['.bib', '.bibyaml', '.bibml', '.yaml']
FORMATS_INPUT = {'bib': pybtex.database.input.bibtex,
                 'xml': pybtex.database.input.bibtexml,
                 'yml': pybtex.database.input.bibyaml,
                 'yaml': pybtex.database.input.bibyaml,
                 'bibyaml': pybtex.database.input.bibyaml}
FORMATS_OUTPUT = {'bib': pybtex.database.output.bibtex,
                  'bibtex': pybtex.database.output.bibtex,
                  'xml': pybtex.database.output.bibtexml,
                  'yml': pybtex.database.output.bibyaml,
                  'yaml': pybtex.database.output.bibyaml,
                  'bibyaml': pybtex.database.output.bibyaml}


def clean_path(path):
    return os.path.abspath(os.path.expanduser(path))


def name_from_path(fullpdfpath, verbose=False):
    name, ext = os.path.splitext(os.path.split(fullpdfpath)[1])
    if verbose:
        if ext != '.pdf' and ext != '.ps':
            print(colored('warning', 'yellow')
                    + '{: extension {ext} not recognized'.format(
                        ext=colored(ext, 'cyan')))
    return name, ext


def check_file(path, fail=False):
    if fail:
        if not os.path.exists(path):
            raise(IOError, "File does not exist: %s." % path)
        if not os.path.isfile(path):
            raise(IOError, "%s is not a file." % path)
        return True
    else:
        return os.path.exists(path) and os.path.isfile(path)


# yaml I/O

def write_yamlfile(filepath, datamap):
    try:
        with open(filepath, 'w') as f:
            yaml.dump(datamap, f)
    except IOError:
        print(colored('error', 'error')
                + ': impossible to read file {}'.format(
                    colored(filepath, 'filepath')))
        exit(-1)


def read_yamlfile(filepath):
    check_file(filepath, fail=True)
    try:
        with open(filepath, 'r') as f:
            return yaml.load(f)
    except IOError:
        print(colored('error', 'error')
                + ': impossible to read file {}'.format(
                    colored(filepath, 'filepath')))
        exit(-1)


def load_bibdata(filename, filepath):
    return load_externalbibfile(filepath)


def write_bibdata(bib_data, file_, format_):
    writer = FORMATS_OUTPUT[format_].Writer()
    writer.write_stream(bib_data, file_)


def save_bibdata(bib_data, filepath):
    with open(filepath, 'w') as f:
        write_bibdata(bib_data, f, 'yaml')


def save_meta(meta_data, filepath):
    write_yamlfile(filepath, meta_data)


# is this function ever used? 08/06/2013
def load_meta(filepath):
    return read_yamlfile(filepath)


# specific to bibliography data

def load_externalbibfile(fullbibpath):
    check_file(fullbibpath, fail=True)
    filename, ext = os.path.splitext(os.path.split(fullbibpath)[1])
    if ext[1:] in FORMATS_INPUT.keys():
        with open(fullbibpath) as f:
            return parse_bibdata(f, ext[1:])
    else:
        print(colored('error', 'error')
                + ': {} not recognized format for bibliography'.format(
                    colored(ext, 'cyan')))
        exit(-1)


def parse_bibdata(content, format_):
    """Parse bib data from string.

    :content: stream
    :param format_: (bib|xml|yml)
    """
    parser = FORMATS_INPUT[format_].Parser()
    return parser.parse_stream(content)


def editor_input(config, initial="", suffix=None):
    """Use an editor to get input"""
    if suffix is None:
        suffix = '.tmp'
    editor = config.get(configs.MAIN_SECTION, 'edit-cmd')
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        tfile_name = temp_file.name
        temp_file.write(initial)
        temp_file.flush()
        subprocess.call([editor, tfile_name])
    with open(tfile_name) as temp_file:
        content = temp_file.read()
        os.remove(tfile_name)
    return content
