import sys
import io
import os
import shutil
import glob
import unittest

import dotdot
from pyfakefs import (fake_filesystem, fake_filesystem_shutil,
                      fake_filesystem_glob)

# pyfakefs uses cStringIO under Python 2.x, which does not accept arbitrary unicode strings
# (see https://docs.python.org/2/library/stringio.html#module-cStringIO)
# io.StringIO does not accept `str`, so we're left with the StringIO module
# PS: this nonsense explains why Python 3.x was created.
try:
    import StringIO
    fake_filesystem.io = StringIO
except ImportError:
    pass

from pubs.p3 import input, _fake_stdio, _get_fake_stdio_ucontent
from pubs import content, filebroker

    # code for fake fs

real_os = os
real_open = open
real_shutil = shutil
real_glob = glob
real_io = io


ENCODING = 'utf8'

class FakeIO(object):

    def __init__(self, fake_open):
        self.fake_open = fake_open

    def open(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True):
        # encoding is ignored by pyfakefs
        # https://github.com/jmcgeheeiv/pyfakefs/blob/master/pyfakefs/fake_filesystem.py#L2143
        return self.fake_open(file, mode=mode, buffering=buffering)


    BytesIO = real_io.BytesIO
    StringIO = real_io.StringIO


def create_fake_fs(module_list):

    fake_fs = fake_filesystem.FakeFilesystem()
    fake_os = fake_filesystem.FakeOsModule(fake_fs)
    fake_open = fake_filesystem.FakeFileOpen(fake_fs)
    fake_shutil = fake_filesystem_shutil.FakeShutilModule(fake_fs)
    fake_glob = fake_filesystem_glob.FakeGlobModule(fake_fs)
    fake_io = FakeIO(fake_open)

    fake_fs.CreateDirectory(fake_os.path.expanduser('~'))

    sys.modules['os']     = fake_os
    sys.modules['shutil'] = fake_shutil
    sys.modules['glob']   = fake_glob
    sys.modules['io']     = fake_io

    for md in module_list:
        md.os = fake_os
        md.shutil = fake_shutil
        md.open = fake_open
        md.file = None
        md.io = fake_io

    return {'fs': fake_fs,
            'os': fake_os,
            'open': fake_open,
            'io': fake_io,
            'shutil': fake_shutil,
            'glob': fake_glob}


def unset_fake_fs(module_list):
    try:
        __builtins__.open = real_open
    except AttributeError:
        __builtins__['open'] = real_open

    sys.modules['os']     = real_os
    sys.modules['shutil'] = real_shutil
    sys.modules['glob']   = real_glob
    sys.modules['io']     = real_io

    for md in module_list:
        md.os = real_os
        md.shutil = real_shutil
        md.open = real_open
        md.io = real_io


def copy_dir(fs, real_dir, fake_dir = None):
    """Copy all the data directory into the fake fs"""
    if fake_dir is None:
        fake_dir = real_dir
    for filename in real_os.listdir(real_dir):
        real_path = os.path.abspath(real_os.path.join(real_dir, filename))
        fake_path = fs['os'].path.join(fake_dir, filename)
        if real_os.path.isfile(real_path):
            _, ext = real_os.path.splitext(filename)
            if ext in ['.yaml', '.bib', '.txt', '.md']:
                with real_io.open(real_path, 'r', encoding='utf-8') as f:
                    fs['fs'].CreateFile(fake_path, contents=f.read())
            else:
                with real_io.open(real_path, 'rb') as f:
                    fs['fs'].CreateFile(fake_path, contents=f.read())

        if real_os.path.isdir(real_path):
            fs['fs'].CreateDirectory(fake_path)
            copy_dir(fs, real_path, fake_path)


# redirecting output

def redirect(f):
    def newf(*args, **kwargs):
        old_stderr, old_stdout = sys.stderr, sys.stdout
        stdout = _fake_stdio()
        stderr = _fake_stdio()
        sys.stdout, sys.stderr = stdout, stderr
        try:
            return f(*args, **kwargs), _get_fake_stdio_ucontent(stdout), _get_fake_stdio_ucontent(stderr)
        finally:
            sys.stderr, sys.stdout = old_stderr, old_stdout
    return newf


# Test helpers

# automating input

real_input = input


class FakeInput():
    """ Replace the input() command, and mock user input during tests

        Instanciate as :
        input = FakeInput(['yes', 'no'])
        then replace the input command in every module of the package :
        input.as_global()
        Then :
        input() returns 'yes'
        input() returns 'no'
        input() raises IndexError
     """

    class UnexpectedInput(Exception):
        pass

    def __init__(self, inputs, module_list=tuple()):
        self.inputs = list(inputs) or []
        self.module_list = module_list
        self._cursor = 0

    def as_global(self):
        for md in self.module_list:
            md.input = self
            md.editor_input = self
            # if mdname.endswith('files'):
            #     md.editor_input = self

    def add_input(self, inp):
        self.inputs.append(inp)

    def __call__(self, *args, **kwargs):
        try:
            inp = self.inputs[self._cursor]
            self._cursor += 1
            return inp
        except IndexError:
            raise self.UnexpectedInput('Unexpected user input in test.')


class TestFakeFs(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    def setUp(self):
        self.fs = create_fake_fs([content, filebroker])

    def tearDown(self):
        unset_fake_fs([content, filebroker])
