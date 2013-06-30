import sys, os
import unittest
import pkgutil

import testenv
import fake_filesystem
import fake_filesystem_shutil

from papers import papers_cmd
from papers import color
from papers.p3 import io

real_os = os
real_open = open

fake_os, fake_open, fake_shutil = None, None, None

def _create_fake_fs():
    global fake_os, fake_open, fake_shutil

    fake_fs = fake_filesystem.FakeFilesystem()
    fake_os = fake_filesystem.FakeOsModule(fake_fs)
    fake_open = fake_filesystem.FakeFileOpen(fake_fs)
    fake_shutil = fake_filesystem_shutil.FakeShutilModule(fake_fs)

    fake_fs.CreateDirectory(fake_os.path.expanduser('~'))
    __builtins__['open'] = fake_open
    __builtins__['file'] = fake_open

    sys.modules['os'] = fake_os
    sys.modules['shutil'] = fake_shutil

    import papers
    for importer, modname, ispkg in pkgutil.walk_packages(
                                        path=papers.__path__,
                                        prefix=papers.__name__+'.',
                                        onerror=lambda x: None):
        md = __import__(modname, fromlist = 'dummy')
        md.os = fake_os
        md.shutil = fake_shutil

    return fake_fs

def _copy_data(fs):
    """Copy all the data directory into the fake fs"""
    for filename in real_os.listdir('data/'):
        filepath = 'data/' + filename
        if real_os.path.isfile(filepath):
            with real_open(filepath, 'r') as f:
                fs.CreateFile(filepath, contents = f.read())
        if real_os.path.isdir(filepath):
            fs.CreateDirectory(filepath)

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

#@redirect
def _execute_cmds(cmds, fs = None):
    if fs is None:
        fs = _create_fake_fs()
        _copy_data(fs)

    outs = []
    for cmd in cmds:
        _, stdout, stderr = redirect(papers_cmd.execute)(cmd.split())
        outs.append(color.undye(stdout.getvalue()))

    return outs


class TestInit(unittest.TestCase):

    def test_init(self):
        fs = _create_fake_fs()
        papers_cmd.execute('papers init -p paper_test2'.split())
        self.assertEqual(set(fake_os.listdir('/paper_test2/')), {'bibdata', 'doc', 'meta', 'papers.yaml'})


class TestAdd(unittest.TestCase):

    def test_add(self):

        fs = _create_fake_fs()
        _copy_data(fs)

        papers_cmd.execute('papers init'.split())
        papers_cmd.execute('papers add -b /data/pagerank.bib -d /data/pagerank.pdf'.split())

    def test_add2(self):

        fs = _create_fake_fs()
        _copy_data(fs)

        papers_cmd.execute('papers init -p /not_default'.split())
        papers_cmd.execute('papers add -b /data/pagerank.bib -d /data/pagerank.pdf'.split())
        self.assertEqual(set(fake_os.listdir('/not_default/doc')), {'Page99.pdf'})


class TestList(unittest.TestCase):

    def test_list(self):

        fs = _create_fake_fs()
        _copy_data(fs)

        papers_cmd.execute('papers init -p /not_default2'.split())
        papers_cmd.execute('papers list'.split())
        papers_cmd.execute('papers add -b /data/pagerank.bib -d /data/pagerank.pdf'.split())
        papers_cmd.execute('papers list'.split())


class TestUsecase(unittest.TestCase):

    def test_first(self):

        correct = ['Initializing papers in /paper_first/.\n',
                   'Added: Page99\n',
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

        self.assertEqual(correct, _execute_cmds(cmds))

    def test_second(self):

        cmds = ['papers init -p paper_second/',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf'
               ]

        _execute_cmds(cmds)

    def test_third(self):

        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf',
                'papers remove -f Page99',
                'papers remove -f turing1950computing',
               ]

        _execute_cmds(cmds)
