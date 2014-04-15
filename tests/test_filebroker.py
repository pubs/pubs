# -*- coding: utf-8 -*-
import unittest
import os

import dotdot
import fake_env

from pubs import content, filebroker


class TestFileBroker(fake_env.TestFakeFs):

    def test_pushpull1(self):

        fb = filebroker.FileBroker('bla', create = True)

        fb.push_metafile('citekey1', 'abc')
        fb.push_bibfile('citekey1', 'cdef')

        self.assertEqual(fb.pull_metafile('citekey1'), 'abc')
        self.assertEqual(fb.pull_bibfile('citekey1'), 'cdef')

        fb.push_bibfile('citekey1', 'ghi')

        self.assertEqual(fb.pull_bibfile('citekey1'), 'ghi')

    def test_existing_data(self):

        fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'tmpdir'), 'tmpdir')
        fb = filebroker.FileBroker('tmpdir', create = True)

        with open('tmpdir/bib/Page99.bib', 'r') as f:
            self.assertEqual(fb.pull_bibfile('Page99'), f.read())

        with open('tmpdir/meta/Page99.yaml', 'r') as f:
            self.assertEqual(fb.pull_metafile('Page99'), f.read())

    def test_errors(self):

        with self.assertRaises(IOError):
            filebroker.FileBroker('tmpdir', create = False)

        fb = filebroker.FileBroker('tmpdir', create = True)
        with self.assertRaises(IOError):
            fb.pull_bibfile('Page99')
        with self.assertRaises(IOError):
            fb.pull_metafile('Page99')

    def test_errors(self):

        with self.assertRaises(IOError):
            filebroker.FileBroker('tmpdir', create = False)

        fb = filebroker.FileBroker('tmpdir', create = True)

        self.assertFalse(fb.exists('Page99'))
        with self.assertRaises(IOError):
            fb.pull_bibfile('Page99')
        with self.assertRaises(IOError):
            fb.pull_metafile('Page99')

    def test_remove(self):

        with self.assertRaises(IOError):
            filebroker.FileBroker('tmpdir', create = False)

        fb = filebroker.FileBroker('tmpdir', create = True)

        fb.push_bibfile('citekey1', 'abc')
        self.assertEqual(fb.pull_bibfile('citekey1'), 'abc')
        fb.push_metafile('citekey1', 'defg')
        self.assertEqual(fb.pull_metafile('citekey1'), 'defg')
        self.assertTrue(fb.exists('citekey1'))

        fb.remove('citekey1')
        with self.assertRaises(IOError):
            self.assertEqual(fb.pull_bibfile('citekey1'), 'abc')
        with self.assertRaises(IOError):
            self.assertEqual(fb.pull_metafile('citekey1'), 'defg')
        self.assertFalse(fb.exists('citekey1'))


class TestDocBroker(fake_env.TestFakeFs):

    def test_doccopy(self):

        fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'data'), 'data')

        fb = filebroker.FileBroker('tmpdir', create = True)
        docb = filebroker.DocBroker('tmpdir')

        docpath = docb.add_doc('Page99', 'data/pagerank.pdf')
        self.assertTrue(content.check_file(os.path.join('tmpdir', 'doc/Page99.pdf')))

        self.assertTrue(docb.in_docsdir(docpath))
        self.assertEqual(docpath,  'docsdir://Page99.pdf')
        docb.remove_doc('docsdir://Page99.pdf')

        self.assertFalse(content.check_file(os.path.join('tmpdir', 'doc/Page99.pdf'), fail=False))
        with self.assertRaises(IOError):
            self.assertFalse(content.check_file(os.path.join('tmpdir', 'doc/Page99.pdf'), fail=True))


if __name__ == '__main__':
    unittest.main()
