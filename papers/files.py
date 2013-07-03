"""
This module can't depend on configs.
If you feel the need to import configs, you are not in the right place.
"""
from __future__ import print_function

import os
import subprocess
import tempfile
from .p3 import io
from io import StringIO

import yaml

from . import ui
from . import color

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
    print(color.dye('error', color.error) +
          ": you need to install Pybtex; try running 'pip install "
          "pybtex' or 'easy_install pybtex'")
    exit(-1)

_papersdir = None

BIB_EXTENSIONS = ['.bib', '.bibyaml', '.bibml', '.yaml']
FORMATS_INPUT =  {'bib'    : pybtex.database.input.bibtex,
                  'xml'    : pybtex.database.input.bibtexml,
                  'yml'    : pybtex.database.input.bibyaml,
                  'yaml'   : pybtex.database.input.bibyaml,
                  'bibyaml': pybtex.database.input.bibyaml}
FORMATS_OUTPUT = {'bib'    : pybtex.database.output.bibtex,
                  'bibtex' : pybtex.database.output.bibtex,
                  'xml'    : pybtex.database.output.bibtexml,
                  'yml'    : pybtex.database.output.bibyaml,
                  'yaml'   : pybtex.database.output.bibyaml,
                  'bibyaml': pybtex.database.output.bibyaml}


def clean_path(*args):
    return os.path.abspath(os.path.expanduser(os.path.join(*args)))


def name_from_path(fullpdfpath, verbose=False):
    name, ext = os.path.splitext(os.path.split(fullpdfpath)[1])
    if verbose:
        if ext != '.pdf' and ext != '.ps':
            print('{}: extension {} not recognized'.format(
                  color.dye('warning', color.warning),
                  color.dye(ext, color.cyan)))
    return name, ext


def check_file(path, fail=False):
    if fail:
        if not os.path.exists(path):
            raise IOError("File does not exist: {}.".format(path))
        if not os.path.isfile(path):
            raise IOError("{} is not a file.".format(path))
        return True
    else:
        return os.path.exists(path) and os.path.isfile(path)


# yaml I/O

def write_yamlfile(filepath, datamap):
    try:
        with open(filepath, 'w') as f:
            yaml.dump(datamap, f)
    except IOError:
        print('{}: impossible to read or write on file {}'.format(
              color.dye('error', color.error),
              color.dye(filepath, color.filepath)))
        exit(-1)


def read_yamlfile(filepath):
    check_file(filepath, fail=True)
    try:
        with open(filepath, 'r') as f:
            return yaml.load(f)
    except IOError:
        print('{}: impossible to read file {}'.format(
              color.dye('error', color.error),
              color.dye(filepath, color.filepath)))
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
    new_meta = meta_data.copy()
    # Cannot store sets in yaml
    new_meta['tags'] = list(new_meta['tags'])
    write_yamlfile(filepath, new_meta)


# is this function ever used? 08/06/2013
def load_meta(filepath):
    return read_yamlfile(filepath)


# specific to bibliography data

def load_externalbibfile(fullbibpath):
    check_file(fullbibpath, fail=True)
    filename, ext = os.path.splitext(os.path.split(fullbibpath)[1])
    if ext[1:] in list(FORMATS_INPUT.keys()):
        with open(fullbibpath) as f:
            return _parse_bibdata_formated_stream(f, ext[1:])
    else:
        print('{}: {} not recognized format for bibliography'.format(
              color.dye('error', color.error),
              color.dye(ext, color.cyan)))
        exit(-1)


def _parse_bibdata_formated_stream(stream, fmt):
    """Parse a stream for bibdata, using the supplied format."""
    try:
        parser = FORMATS_INPUT[fmt].Parser()
        data = parser.parse_stream(stream)
        if len(list(data.entries.keys())) > 0:
            return data
    except Exception:
        pass
    raise ValueError('content format is not recognized.')

def parse_bibdata(content, format_ = None):
    """Parse bib data from string or stream.

    Raise ValueError if no bibdata is present.
    :content: stream
    :param format_: (bib|xml|yml) if format is None, tries to recognize the
                    format automatically.
    """
    fmts = [format_]
    if format_ is None:
        fmts = FORMATS_INPUT.keys()
        # we need to reuse the content
        content = content if type(content) == str else str(content.read())

    # If you use StingIO from io then the content must be unicode
    # Let call this quick fix a hack but we should think it more carefully
    content = unicode(content)
    # This bug was really a pain in the ass to discover because of the (old) except Expection below!
    # I changed it to the only kind of error that can raise _parse_bibdata_formated_stream, which is a ValueError

    for fmt in fmts:
        try:
            return _parse_bibdata_formated_stream(StringIO(content), fmt)
        except ValueError:
            pass

    raise ValueError('content format is not recognized.')


def editor_input(editor, initial="", suffix=None):
    """Use an editor to get input"""
    if suffix is None:
        suffix = '.tmp'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        tfile_name = temp_file.name
        temp_file.write(initial)
        temp_file.flush()
        subprocess.call([editor, tfile_name])
    with open(tfile_name) as temp_file:
        content = temp_file.read()
        os.remove(tfile_name)
    return content
