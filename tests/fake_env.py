import sys
import io
import os
import shutil
import glob
import unittest

import dotdot
import fake_filesystem
import fake_filesystem_shutil
import fake_filesystem_glob

from pubs.p3 import input
from pubs import content, filebroker

    # code for fake fs

real_os = os
real_open = open
real_file = file
real_shutil = shutil
real_glob = glob
real_io = io



# def _mod_list():
#     ml = []
#     import pubs
#     for importer, modname, ispkg in pkgutil.walk_packages(
#                                         path=pubs.__path__,
#                                         prefix=pubs.__name__ + '.',
#                                         onerror=lambda x: None):
#         # HACK to not load textnote
#         if not modname.startswith('pubs.plugs.texnote'):
#             ml.append((modname, __import__(modname, fromlist='dummy')))
#     return ml


ENCODING = 'utf8'


class UnicodeStringIOWrapper(object):
    """This is a hack because fake_filesystem does not provied mock of io.
    """

    override = ['read', 'readline', 'readlines', 'write', 'writelines']

    def __init__(self, strio):
        self._strio = strio  # The real StringIO

    def __getattr__(self, name):
        if name in UnicodeStringIOWrapper.override:
            return object.__getattribute__(self, name)
        else:
            return self._strio.__getattribute__(name)

    def read(self, *args):
        return self._strio.read(*args).decode(ENCODING)

    def readline(self, *args):
        return self._strio.readline(*args).decode(ENCODING)

    def readlines(self, *args):
        return [l.decode(ENCODING) for l in self._strio.readlines(*args)]

    def write(self, data):
        self._strio.write(data.encode(ENCODING))

    def writelines(self, data):
        self._strio.write([l.encode(ENCODING) for l in data])

    def __enter__(self):
        self._strio.__enter__()
        return self

    def __exit__(self, *args):
        return self._strio.__exit__(*args)


class FakeIO(object):

    def __init__(self, fake_open):
        self.fake_open = fake_open

    def open(self, *args, **kwargs):
        # Forces python3 mode for FakeFileOpen
        fakefs_stringio = self.fake_open.Call(*args, **kwargs)
        return UnicodeStringIOWrapper(fakefs_stringio)


def create_fake_fs(module_list):

    fake_fs = fake_filesystem.FakeFilesystem()
    fake_os = fake_filesystem.FakeOsModule(fake_fs)
    fake_open = fake_filesystem.FakeFileOpen(fake_fs)
    fake_shutil = fake_filesystem_shutil.FakeShutilModule(fake_fs)
    fake_glob = fake_filesystem_glob.FakeGlobModule(fake_fs)
    fake_io = FakeIO(fake_open)

    fake_fs.CreateDirectory(fake_os.path.expanduser('~'))

    __builtins__.update({'open': fake_open, 'file': fake_open})

    sys.modules['os']     = fake_os
    sys.modules['shutil'] = fake_shutil
    sys.modules['glob']   = fake_glob
    sys.modules['io']     = fake_io

    for md in module_list:
        md.os = fake_os
        md.shutil = fake_shutil
        md.open = fake_open
        md.file = fake_open
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
        __builtins__.file = real_file
    except AttributeError:
        __builtins__['open'] = real_open
        __builtins__['file'] = real_file

    sys.modules['os']     = real_os
    sys.modules['shutil'] = real_shutil
    sys.modules['glob']   = real_glob
    sys.modules['io']     = real_io

    for md in module_list:
        md.os = real_os
        md.shutil = real_shutil
        md.open = real_open
        md.file = real_file
        md.io = real_io


def copy_dir(fs, real_dir, fake_dir = None):
    """Copy all the data directory into the fake fs"""
    if fake_dir is None:
        fake_dir = real_dir
    for filename in real_os.listdir(real_dir):
        real_path = os.path.abspath(real_os.path.join(real_dir, filename))
        fake_path = fs['os'].path.join(fake_dir, filename)
        if real_os.path.isfile(real_path):
            with real_open(real_path, 'rb') as f:
                fs['fs'].CreateFile(fake_path, contents=f.read())
        if real_os.path.isdir(real_path):
            fs['fs'].CreateDirectory(fake_path)
            copy_dir(fs, real_path, fake_path)


# redirecting output

def redirect(f):
    def newf(*args, **kwargs):
        old_stderr, old_stdout = sys.stderr, sys.stdout
        stdout = io.BytesIO()
        stderr = io.BytesIO()
        sys.stdout, sys.stderr = stdout, stderr
        try:
            return f(*args, **kwargs), stdout, stderr
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
        input() raise IndexError
     """

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
        inp = self.inputs[self._cursor]
        self._cursor += 1
        return inp


class TestFakeFs(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    def setUp(self):
        self.fs = create_fake_fs([content, filebroker])

    def tearDown(self):
        unset_fake_fs([content, filebroker])
