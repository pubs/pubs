# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
import shutil

import yaml
from pybtex.database import Person

import fixtures
from papers.paper import Paper


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
external-document: null
notes: []
tags: []
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
        self.dest_bibfile = os.path.join(self.tmpdir, 'written_bib.yaml')
        self.dest_metafile = os.path.join(self.tmpdir, 'written_meta.yaml')

    def test_load_valid(self):
        p = Paper.load(self.bibfile, metapath=self.metafile)
        self.assertEqual(fixtures.turing1950, p)

    def test_save_fails_with_no_citekey(self):
        p = Paper()
        with self.assertRaises(ValueError):
            p.save_to_disc(self.dest_bibfile, self.dest_metafile)

    def test_save_creates_bib(self):
        fixtures.turing1950.save_to_disc(self.dest_bibfile, self.dest_metafile)
        self.assertTrue(os.path.exists(self.dest_bibfile))

    def test_save_creates_meta(self):
        fixtures.turing1950.save_to_disc(self.dest_bibfile, self.dest_metafile)
        self.assertTrue(os.path.exists(self.dest_metafile))

    def test_save_right_bib(self):
        fixtures.turing1950.save_to_disc(self.dest_bibfile, self.dest_metafile)
        with open(self.dest_bibfile, 'r') as f:
            written = yaml.load(f)
            ok = yaml.load(BIB)
            self.assertEqual(written, ok)

    def test_save_right_meta(self):
        fixtures.turing1950.save_to_disc(self.dest_bibfile, self.dest_metafile)
        with open(self.dest_metafile, 'r') as f:
            written = yaml.load(f)
            ok = yaml.load(META)
            self.assertEqual(written, ok)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestCopy(unittest.TestCase):

    def setUp(self):
        self.orig = Paper()
        self.orig.bibentry.fields['title'] = u'Nice title.'
        self.orig.bibentry.fields['year'] = u'2013'
        self.orig.bibentry.persons['author'] = [Person(u'John Doe')]
        self.orig.citekey = self.orig.generate_citekey()

    def test_copy_equal(self):
        copy = self.orig.copy()
        self.assertEqual(copy, self.orig)

    def test_copy_can_be_changed(self):
        copy = self.orig.copy()
        copy.bibentry.fields['year'] = 2014
        self.assertEqual(self.orig.bibentry.fields['year'], u'2013')
