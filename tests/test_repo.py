import unittest
import tempfile
import shutil
import os

import fixtures
from papers.repo import Repository, _str_incr, _to_suffix, BIB_DIR, META_DIR


class TestCitekeyGeneration(unittest.TestCase):

    def test_string_increment(self):
        l = []
        self.assertEqual(_to_suffix(l), '')
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'a')
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'b')
        l = ['z']
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'aa')

    def test_generated_key_is_unique(self):
        repo = Repository()
        repo.add_paper(fixtures.turing1950)
        repo.add_paper(fixtures.doe2013)
        c = repo.get_free_citekey(fixtures.turing1950)
        self.assertEqual(c, 'Turing1950a')
        fixtures.turing1950.citekey = 'Turing1950a'
        repo.add_paper(fixtures.turing1950)
        c = repo.get_free_citekey(fixtures.turing1950)
        self.assertEqual(c, 'Turing1950b')


class TestAddPaper(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo = Repository(papersdir=self.tmpdir)
        self.repo.init()
        self.repo.add_paper(fixtures.turing1950)

    def test_raises_value_error_on_existing_key(self):
        with self.assertRaises(ValueError):
            self.repo.add_paper(fixtures.turing1950)

    def test_saves_bib(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, BIB_DIR,
            'Turing1950.bibyaml')))

    def test_saves_meta(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, META_DIR,
            'Turing1950.meta')))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
