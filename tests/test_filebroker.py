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

        self.fs.add_real_directory(os.path.join(self.rootpath, 'testrepo'), read_only=False)
        fb = filebroker.FileBroker('testrepo', create = True)

        bib_content = content.read_text_file('testrepo/bib/Page99.bib')
        self.assertEqual(fb.pull_bibfile('Page99'), bib_content)

        meta_content = content.read_text_file('testrepo/meta/Page99.yaml')
        self.assertEqual(fb.pull_metafile('Page99'), meta_content)

    def test_errors(self):

        with self.assertRaises(IOError):
            filebroker.FileBroker('testrepo', create = False)

        fb = filebroker.FileBroker('testrepo', create = True)

        self.assertFalse(fb.exists('Page99'))
        with self.assertRaises(IOError):
            fb.pull_bibfile('Page99')
        with self.assertRaises(IOError):
            fb.pull_metafile('Page99')

    def test_remove(self):

        with self.assertRaises(IOError):
            filebroker.FileBroker('testrepo', create = False)

        fb = filebroker.FileBroker('testrepo', create = True)

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

        self.fs.add_real_directory(os.path.join(self.rootpath, 'data'), read_only=False)

        fb = filebroker.FileBroker('testrepo', create = True)
        docb = filebroker.DocBroker('testrepo')

        docpath = docb.add_doc('Page99', 'data/pagerank.pdf')
        self.assertTrue(content.check_file(os.path.join('testrepo', 'doc/Page99.pdf')))

        self.assertTrue(docb.in_docsdir(docpath))
        self.assertEqual(docpath,  'docsdir://Page99.pdf')
        docb.remove_doc('docsdir://Page99.pdf')

        self.assertFalse(content.check_file(os.path.join('testrepo', 'doc/Page99.pdf'), fail=False))
        with self.assertRaises(IOError):
            self.assertFalse(content.check_file(os.path.join('testrepo', 'doc/Page99.pdf'), fail=True))


if __name__ == '__main__':
    unittest.main()
