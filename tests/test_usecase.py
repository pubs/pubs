import sys
import os
import shutil
import glob
import unittest
import pkgutil
import re

import testenv
import fake_filesystem
import fake_filesystem_shutil
import fake_filesystem_glob

from papers import papers_cmd
from papers import color, files
from papers.p3 import io, input

import fixtures


    # code for fake fs

real_os = os
real_open = open
real_shutil = shutil
real_glob = glob

fake_os, fake_open, fake_shutil, fake_glob = None, None, None, None


def _mod_list():
    ml = []
    import papers
    for importer, modname, ispkg in pkgutil.walk_packages(
                                        path=papers.__path__,
                                        prefix=papers.__name__ + '.',
                                        onerror=lambda x: None):
        # HACK to not load textnote
        if not modname.startswith('papers.plugs.texnote'):
            ml.append((modname, __import__(modname, fromlist='dummy')))
    return ml

mod_list = _mod_list()


def _create_fake_fs():
    global fake_os, fake_open, fake_shutil, fake_glob

    fake_fs = fake_filesystem.FakeFilesystem()
    fake_os = fake_filesystem.FakeOsModule(fake_fs)
    fake_open = fake_filesystem.FakeFileOpen(fake_fs)
    fake_shutil = fake_filesystem_shutil.FakeShutilModule(fake_fs)
    fake_glob = fake_filesystem_glob.FakeGlobModule(fake_fs)

    fake_fs.CreateDirectory(fake_os.path.expanduser('~'))

    try:
        __builtins__.open = fake_open
        __builtins__.file = fake_open
    except AttributeError:
        __builtins__['open'] = fake_open
        __builtins__['file'] = fake_open

    sys.modules['os']     = fake_os
    sys.modules['shutil'] = fake_shutil
    sys.modules['glob']   = fake_glob

    for mdname, md in mod_list:
        md.os = fake_os
        md.shutil = fake_shutil
        md.open = fake_open
        md.file = fake_open

    return fake_fs


def _copy_data(fs):
    """Copy all the data directory into the fake fs"""
    datadir = real_os.path.join(real_os.path.dirname(__file__), 'data')
    for filename in real_os.listdir(datadir):
        real_path = real_os.path.join(datadir, filename)
        fake_path = fake_os.path.join('data', filename)
        if real_os.path.isfile(real_path):
            with real_open(real_path, 'r') as f:
                fs.CreateFile(fake_path, contents=f.read())
        if real_os.path.isdir(real_path):
            fs.CreateDirectory(fake_path)


    # redirecting output

def redirect(f):
    def newf(*args, **kwargs):
        old_stderr, old_stdout = sys.stderr, sys.stdout
        stdout = io.StringIO()
        stderr = io.StringIO()
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

    def __init__(self, inputs=None):
        self.inputs = list(inputs) or []
        self._cursor = 0

    def as_global(self):
        for mdname, md in mod_list:
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


class TestFakeInput(unittest.TestCase):

    def test_input(self):

        input = FakeInput(['yes', 'no'])
        self.assertEqual(input(), 'yes')
        self.assertEqual(input(), 'no')
        with self.assertRaises(IndexError):
            input()

    def test_input2(self):
        other_input = FakeInput(['yes', 'no'])
        other_input.as_global()
        self.assertEqual(color.input(), 'yes')
        self.assertEqual(color.input(), 'no')
        with self.assertRaises(IndexError):
            color.input()

    def test_editor_input(self):
        other_input = FakeInput(['yes', 'no'])
        other_input.as_global()
        self.assertEqual(files.editor_input(), 'yes')
        self.assertEqual(files.editor_input(), 'no')
        with self.assertRaises(IndexError):
            color.input()


class CommandTestCase(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    def setUp(self):
        self.fs = _create_fake_fs()

    def execute_cmds(self, cmds, fs=None):
        """ Execute a list of commands, and capture their output

        A command can be a string, or a tuple of size 2 or 3.
        In the latter case, the command is :
        1. a string reprensenting the command to execute
        2. the user inputs to feed to the command during execution
        3. the output excpected, verified with assertEqual

        """
        outs = []
        for cmd in cmds:
            if hasattr(cmd, '__iter__'):
                if len(cmd) == 2:
                    input = FakeInput(cmd[1])
                    input.as_global()

                _, stdout, stderr = redirect(papers_cmd.execute)(cmd[0].split())
                if len(cmd) == 3:
                    actual_out  = color.undye(stdout.getvalue())
                    correct_out = color.undye(cmd[2])
                    self.assertEqual(actual_out, correct_out)

            else:
                assert type(cmd) == str
                _, stdout, stderr = redirect(papers_cmd.execute)(cmd.split())

            assert(stderr.getvalue() == '')
            outs.append(color.undye(stdout.getvalue()))
        return outs


class DataCommandTestCase(CommandTestCase):
    """Abstract TestCase intializing the fake filesystem and
    copying fake data.
    """

    def setUp(self):
        CommandTestCase.setUp(self)
        _copy_data(self.fs)


# Actual tests

class TestInit(CommandTestCase):

    def test_init(self):
        papers_cmd.execute('papers init -p paper_test2'.split())
        self.assertEqual(set(fake_os.listdir('/paper_test2/')),
                         {'bibdata', 'doc', 'meta', 'papers.yaml'})


class TestAdd(DataCommandTestCase):

    def test_add(self):
        cmds = ['papers init',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)

    def test_add2(self):
        cmds = ['papers init -p /not_default',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(fake_os.listdir('/not_default/doc')), {'Page99.pdf'})


class TestList(DataCommandTestCase):

    def test_list(self):
        cmds = ['papers init -p /not_default2',
                'papers list',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                'papers list',
                ]
        self.execute_cmds(cmds)


class TestUsecase(DataCommandTestCase):

    def test_first(self):
        correct = ['Initializing papers in /paper_first.\n',
                   '',
                   '0: [Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) \n',
                   '',
                   '',
                   'search network\n',
                   '0: [Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) search network\n',
                   'search network\n']

        cmds = ['papers init -p paper_first/',
                'papers add -d data/pagerank.pdf -b data/pagerank.bib',
                'papers list',
                'papers tag',
                'papers tag Page99 network+search',
                'papers tag Page99',
                'papers tag search',
                'papers tag 0',
               ]

        self.assertEqual(correct, self.execute_cmds(cmds))

    def test_second(self):
        cmds = ['papers init -p paper_second/',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf'
               ]
        self.execute_cmds(cmds)

    def test_third(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf',
                ('papers remove Page99', ['y']),
                'papers remove -f turing1950computing',
               ]
        self.execute_cmds(cmds)

    def test_editor_abort(self):
        with self.assertRaises(SystemExit):
            cmds = ['papers init',
                    ('papers add', ['abc', 'n']),
                    ('papers add', ['abc', 'y', 'abc', 'n']),
                    'papers add -b data/pagerank.bib',
                    ('papers edit Page99', ['', 'a']),
                   ]
            self.execute_cmds(cmds)

    def test_editor_success(self):
        cmds = ['papers init',
                ('papers add', [fixtures.pagerankbib]),
                ('papers remove Page99', ['y']),
               ]
        self.execute_cmds(cmds)

    def test_edit(self):
        bib = fixtures.pagerankbib
        bib1 = re.sub('year = \{1999\}', 'year = {2007}', bib)
        bib2 = re.sub('Lawrence Page', 'Lawrence Ridge', bib1)
        bib3 = re.sub('Page99', 'Ridge07', bib2)

        line = '0: [Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) \n'
        line1 = re.sub('1999', '2007', line)
        line2 = re.sub('L. Page', 'L. Ridge', line1)
        line3 = re.sub('Page99', 'Ridge07', line2)

        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                ('papers list', [], line),
                ('papers edit Page99', [bib1]),
                ('papers list', [], line1),
                ('papers edit Page99', [bib2]),
                ('papers list', [], line2),
                ('papers edit Page99', [bib3]),
                ('papers list', [], line3),
               ]

        self.execute_cmds(cmds)

    def test_export(self):
        cmds = ['papers init',
                ('papers add', [fixtures.pagerankbib]),
                'papers export Page99',
                ('papers export Page99 -f bibtex', [], fixtures.pagerankbib_generated),
                'papers export Page99 -f bibyaml',
               ]

        self.execute_cmds(cmds)

    def test_import(self):
        cmds = ['papers init',
                'papers import data/',
                'papers list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(4 + 1, len(outs[-1].split('\n')))

    def test_import_one(self):
        cmds = ['papers init',
                'papers import data/ Page99',
                'papers list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_open(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers open Page99'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)

        with self.assertRaises(SystemExit):
            cmds[-1] == 'papers open Page8'
            self.execute_cmds(cmds)

    def test_update(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers update'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)
