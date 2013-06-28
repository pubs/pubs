import sys, os
import unittest
import pkgutil

import testenv
import fake_filesystem

import papers
from papers import papers_cmd

def create_fake_fs():
    fake_fs = fake_filesystem.FakeFilesystem()
    fake_os = fake_filesystem.FakeOsModule(fake_fs)
    fake_open = fake_filesystem.FakeFileOpen(fake_fs)
    fake_fs.CreateFile('/Users/fabien/bla')
    __builtins__['open'] = fake_open
    __builtins__['file'] = fake_open

    for importer, modname, ispkg in pkgutil.walk_packages(path=papers.__path__,
                                                      prefix=papers.__name__+'.',
                                                      onerror=lambda x: None):
        md = __import__(modname, fromlist = 'dummy')
        md.os = fake_os


class TestUseCases(unittest.TestCase):

    def test_init(self):
        create_fake_fs()
        papers_md.execute_papers('papers init -p paper_test2'.split())

    def test_init(self):
        create_fake_fs()
        papers_cmd.execute('papers init -p paper_test2'.split())


