# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
import shutil

import yaml
from pybtex.database import Person

from papers.paper import Paper
from papers import files


BIB = """
entries:
    Turing1950:
        author:
        -   first: 'Alan'
            last: 'Turing'
        title: 'Computing machinery and intelligence.'
        type: article
        year: '1950'
"""
META = """
filename: null
extension: null
notes: []
path: null
"""


class TestCreateCitekey(unittest.TestCase):

    def test_fails_on_empty_paper(self):
        paper = Paper()
        with self.assertRaises(ValueError):
            paper.generate_citekey()

    def test_escapes_chars(self):
        paper = Paper()
        paper.bibentry.persons['author'] = [
                Person(last=u'Z ôu\\@/', first='Zde'),
                Person(string='John Doe')]
        key = paper.generate_citekey()
        self.assertEqual(key, 'Zou')

    def test_simple(self):
        paper = Paper()
        paper.bibentry.persons['author'] = [Person(string='John Doe')]
        paper.bibentry.fields['year'] = '2001'
        key = paper.generate_citekey()
        self.assertEqual(key, 'Doe2001')


class TestSaveLoad(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmpdir, 'bibdata'))
        os.makedirs(os.path.join(self.tmpdir, 'meta'))
        self.bibfile = os.path.join(self.tmpdir, 'bib.bibyaml')
        with open(self.bibfile, 'w') as f:
            f.write(BIB)
        self.metafile = os.path.join(self.tmpdir, 'meta.meta')
        with open(self.metafile, 'w') as f:
            f.write(META)
        self.turing1950 = Paper()
        self.turing1950.bibentry.fields['title'] = u'Computing machinery and intelligence.'
        self.turing1950.bibentry.fields['year'] = u'1950'
        self.turing1950.bibentry.persons['author'] = [Person(u'Alan Turing')]
        self.turing1950.citekey = self.turing1950.generate_citekey()

    def test_load_valid(self):
        p = Paper.load(self.bibfile, self.metafile)
        self.assertEqual(self.turing1950, p)

    def test_save_fails_with_no_citekey(self):
        p = Paper()
        with self.assertRaises(ValueError):
            p.save_to_disc(self.tmpdir)

    def test_save_creates_bib(self):
        self.turing1950.save_to_disc(self.tmpdir)
        bibfile = files.path_to_paper_file('Turing1950', 'bib',
                path_to_repo=self.tmpdir)
        self.assertTrue(os.path.exists(bibfile))

    def test_save_creates_meta(self):
        self.turing1950.save_to_disc(self.tmpdir)
        metafile = files.path_to_paper_file('Turing1950', 'meta',
                path_to_repo=self.tmpdir)
        self.assertTrue(os.path.exists(metafile))

    def test_save_right_bib(self):
        self.turing1950.save_to_disc(self.tmpdir)
        bibfile = files.path_to_paper_file('Turing1950', 'bib',
                path_to_repo=self.tmpdir)
        with open(bibfile, 'r') as f:
            written = yaml.load(f)
            ok = yaml.load(BIB)
            self.assertEqual(written, ok)

    def test_save_right_meta(self):
        self.turing1950.save_to_disc(self.tmpdir)
        metafile = files.path_to_paper_file('Turing1950', 'meta',
                path_to_repo=self.tmpdir)
        with open(metafile, 'r') as f:
            written = yaml.load(f)
            ok = yaml.load(META)
            self.assertEqual(written, ok)

    def teardown(self):
        shutil.rmtree(self.tmpdir)
