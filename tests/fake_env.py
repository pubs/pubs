import sys
import io
import os
import shutil
import glob

import dotdot
from pyfakefs import (fake_filesystem, fake_filesystem_shutil,
                      fake_filesystem_glob, fake_filesystem_unittest)

from pubs.p3 import input, _fake_stdio, _get_fake_stdio_ucontent
from pubs import content, filebroker

# code for fake fs

real_os      = os
real_os_path = os.path
real_open    = open
real_shutil  = shutil
real_glob    = glob
real_io      = io


def copy_dir(fs, real_dir, fake_dir=None):
    """Copy all the data directory into the fake fs"""
    if fake_dir is None:
        fake_dir = real_dir

    for filename in real_os.listdir(real_dir):
        real_path = real_os.path.join(real_dir, filename)
        fake_path = os.path.join(fake_dir, filename)
        if real_os.path.isfile(real_path):
            _, ext = real_os.path.splitext(filename)
            if ext in ['.yaml', '.bib', '.txt', '.md']:
                with real_io.open(real_path, 'r', encoding='utf-8') as f:
                    fs.CreateFile(os.path.abspath(fake_path), contents=f.read())
            else:
                with real_io.open(real_path, 'rb') as f:
                    fs.CreateFile(fake_path, contents=f.read())

        if real_os.path.isdir(real_path):
            fs.CreateDirectory(fake_path)
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


class TestFakeFs(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateDirectory(os.path.expanduser('~'))

    def reset_fs(self):
        self._stubber.tearDown()  # renew the filesystem
        self.setUp()
