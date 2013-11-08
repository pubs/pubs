# -*- coding: utf-8 -*-
import unittest
import os

import testenv
import fake_env

from papers import filebroker

class TestFakeFs(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    def setUp(self):
        self.fs = fake_env.create_fake_fs([filebroker])

    def tearDown(self):
        fake_env.unset_fake_fs([filebroker])


class TestEnDecode(TestFakeFs):

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

        with open('tmpdir/bib/Page99.bibyaml', 'r') as f:
            self.assertEqual(fb.pull_bibfile('Page99'), f.read())

        with open('tmpdir/meta/Page99.yaml', 'r') as f:
            self.assertEqual(fb.pull_metafile('Page99'), f.read())
