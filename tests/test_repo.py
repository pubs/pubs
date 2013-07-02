import unittest
import tempfile
import shutil
import os

import testenv
import fixtures
from papers.repo import (Repository, _base27, BIB_DIR, META_DIR,
                         CiteKeyAlreadyExists)
from papers.paper import PaperInRepo
from papers import configs

class TestCitekeyGeneration(unittest.TestCase):

    def test_string_increment(self):
        self.assertEqual(_base27(0), '')
        for i in range(26):
            self.assertEqual(_base27(i+1), chr(97+i))
            self.assertEqual(_base27(26+i+1), 'a' + chr(97+i))

    def test_generated_key_is_unique(self):
        repo = Repository(configs.Config())
        repo.citekeys = ['Turing1950', 'Doe2003']
        c = repo.generate_citekey(fixtures.turing1950)
        repo.citekeys.append('Turing1950a')
        c = repo.generate_citekey(fixtures.turing1950)
        self.assertEqual(c, 'Turing1950b')


class TestRepo(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo = Repository(configs.Config())
        self.repo.init(self.tmpdir)
        self.repo.add_paper(fixtures.turing1950)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestAddPaper(TestRepo):

    def test_raises_value_error_on_existing_key(self):
        with self.assertRaises(ValueError):
            self.repo.add_paper(fixtures.turing1950)

    def test_saves_bib(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, BIB_DIR,
            'Turing1950.bibyaml')))

    def test_saves_meta(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, META_DIR,
            'Turing1950.meta')))


class TestUpdatePaper(TestRepo):

    def test_raises_value_error_on_unknown_paper(self):
        with self.assertRaises(ValueError):
            self.repo.update(fixtures.doe2013)
        with self.assertRaises(ValueError):
            self.repo.update(fixtures.doe2013, old_citekey='zou')

    def test_error_on_existing_destination(self):
        self.repo.add_paper(fixtures.doe2013)
        with self.assertRaises(CiteKeyAlreadyExists):
            self.repo.update(fixtures.turing1950, old_citekey='Doe2013')

    def test_updates_same_key(self):
        new = self.repo.get_paper('Turing1950')
        new.bibentry.fields['journal'] = u'Mind'
        self.repo.update(new)
        self.assertEqual(new, self.repo.get_paper('Turing1950'))

    def test_updates_same_key_with_old_arg(self):
        new = self.repo.get_paper('Turing1950')
        new.bibentry.fields['journal'] = u'Mind'
        self.repo.update(new, old_citekey='Turing1950')
        self.assertEqual(new, self.repo.get_paper('Turing1950'))

    def test_update_new_key_removes_old(self):
        self.repo.update(fixtures.doe2013, old_citekey='Turing1950')
        self.assertFalse(self.repo.has_paper('Turing1950'))

    def test_update_new_key_updates(self):
        self.repo.update(fixtures.doe2013, old_citekey='Turing1950')
        self.assertTrue(self.repo.has_paper('Doe2013'))
        self.assertEqual(self.repo.get_paper('Doe2013'),
                         PaperInRepo.from_paper(fixtures.doe2013, self.repo))

    def test_update_new_key_moves_doc(self):
        self.repo.import_document('Turing1950',
                                  os.path.join(os.path.dirname(__file__),
                                               'data/pagerank.pdf'))
        self.repo.update(fixtures.doe2013, old_citekey='Turing1950')
        self.assertFalse(os.path.exists(os.path.join(
            self.repo.get_document_directory(), 'Turing1950.pdf')))
        self.assertTrue(os.path.exists(os.path.join(
            self.repo.get_document_directory(), 'Doe2013.pdf')))
