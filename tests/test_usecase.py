import sys, os
import unittest
import pkgutil

import testenv
import fake_filesystem
import fake_filesystem_shutil

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


class TestInit(unittest.TestCase):

    def test_init(self):
        fs = _create_fake_fs()
        from papers import papers_cmd
        papers_cmd.execute('papers init -p paper_test2'.split())
        self.assertEqual(set(fake_os.listdir('/paper_test2/')), {'bibdata', 'doc', 'meta', 'papers.yaml'})


class TestAdd(unittest.TestCase):

    def test_add(self):

        fs = _create_fake_fs()
        _copy_data(fs)

        from papers import papers_cmd
        papers_cmd.execute('papers init'.split())
        papers_cmd.execute('papers add -b /data/pagerank.bib -d /data/pagerank.pdf'.split())

    def test_add2(self):

        fs = _create_fake_fs()
        _copy_data(fs)

        from papers import papers_cmd
        papers_cmd.execute('papers init -p /not_default'.split())
        papers_cmd.execute('papers add -b /data/pagerank.bib -d /data/pagerank.pdf'.split())


#class TestAdd2(unittest.TestCase):


