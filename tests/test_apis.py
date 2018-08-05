# coding: utf8

from __future__ import unicode_literals
import unittest

import dotdot

from pubs.p3 import ustr
from pubs.endecoder import EnDecoder
from pubs.apis import ReferenceNotFoundError, arxiv2bibtex, doi2bibtex, isbn2bibtex, _is_arxiv_oldstyle, _extract_arxiv_id

from pubs import apis


class TestDOI2Bibtex(unittest.TestCase):

    def setUp(self):
        self.endecoder = EnDecoder()

    def test_unicode(self):
        bib = doi2bibtex('10.1007/BF01700692')
        self.assertIsInstance(bib, ustr)
        self.assertIn('Kurt Gödel', bib)

    def test_parses_to_bibtex(self):
        bib = doi2bibtex('10.1007/BF01700692')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Gödel, Kurt')
        self.assertEqual(entry['title'],
                         'Über formal unentscheidbare Sätze der Principia '
                         'Mathematica und verwandter Systeme I')

    def test_retrieve_fails_on_incorrect_DOI(self):
        with self.assertRaises(apis.ReferenceNotFoundError):
            doi2bibtex('999999')


class TestISBN2Bibtex(unittest.TestCase):

    def setUp(self):
        self.endecoder = EnDecoder()

    def test_unicode(self):
        bib = isbn2bibtex('9782081336742')
        self.assertIsInstance(bib, ustr)
        self.assertIn('Poincaré, Henri', bib)

    def test_parses_to_bibtex(self):
        bib = isbn2bibtex('9782081336742')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Poincaré, Henri')
        self.assertEqual(entry['title'], 'La science et l\'hypothèse')

    def test_retrieve_fails_on_incorrect_ISBN(self):
        bib = isbn2bibtex('9' * 13)
        with self.assertRaises(EnDecoder.BibDecodingError):
            self.endecoder.decode_bibdata(bib)


class TestArxiv2Bibtex(unittest.TestCase):

    def setUp(self):
        self.endecoder = EnDecoder()

    def test_parses_to_bibtex_with_doi(self):
        bib = arxiv2bibtex('astro-ph/9812133')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Perlmutter, S.')
        self.assertEqual(entry['year'], '1999')

    def test_parses_to_bibtex_without_doi(self):
        bib = arxiv2bibtex('math/0211159')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Perelman, Grisha')
        self.assertEqual(entry['year'], '2002')
        self.assertEqual(
                entry['title'],
                'The entropy formula for the Ricci flow and its geometric applications')

    def test_oldstyle_pattern(self):
        """Test that we can accurately differentiate between old and new style arXiv ids."""
        # old-style arXiv ids
        for arxiv_id in ['cs/9301113', 'math/9201277v3', 'astro-ph/9812133',
                         'cond-mat/0604612', 'hep-ph/0702007v10', 'arXiv:physics/9403001'
                        ]:
            self.assertTrue(_is_arxiv_oldstyle(arxiv_id))
        # new-style arXiv ids
        for arxiv_id in ['1808.00954', 'arXiv:1808.00953', '1808.0953',
                         '1808.00954v1', 'arXiv:1808.00953v2', '1808.0953v42']:
            self.assertFalse(_is_arxiv_oldstyle(arxiv_id))

    def test_extract_id(self):
        """Test that ids are correctly extracted"""
        self.assertEqual(_extract_arxiv_id({'id': "http://arxiv.org/abs/0704.0010v1"}), "0704.0010v1")
        self.assertEqual(_extract_arxiv_id({'id': "https://arxiv.org/abs/0704.0010v1"}), "0704.0010v1")
        self.assertEqual(_extract_arxiv_id({'id': "https://arxiv.org/abs/astro-ph/9812133v2"}), "astro-ph/9812133v2")

if __name__ == '__main__':
    unittest.main(verbosity=2)
