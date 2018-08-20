# coding: utf8

from __future__ import unicode_literals
import unittest

import mock


import dotdot

from pubs.p3 import ustr
from pubs.endecoder import EnDecoder
from pubs.apis import ReferenceNotFoundError, arxiv2bibtex, doi2bibtex, isbn2bibtex, _is_arxiv_oldstyle, _extract_arxiv_id

from pubs import apis

import mock_requests


class APITests(unittest.TestCase):

    def setUp(self):
        self.endecoder = EnDecoder()


class TestDOI2Bibtex(APITests):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_unicode(self, reqget):
        bib = doi2bibtex('10.1007/BF01700692')
        self.assertIsInstance(bib, ustr)
        self.assertIn('Kurt Gödel', bib)

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex(self, reqget):
        bib = doi2bibtex('10.1007/BF01700692')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Gödel, Kurt')
        self.assertEqual(entry['title'],
                         'Über formal unentscheidbare Sätze der Principia '
                         'Mathematica und verwandter Systeme I')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_retrieve_fails_on_incorrect_DOI(self, reqget):
        with self.assertRaises(apis.ReferenceNotFoundError):
            doi2bibtex('999999')


class TestISBN2Bibtex(APITests):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_unicode(self, reqget):
        bib = isbn2bibtex('9782081336742')
        self.assertIsInstance(bib, ustr)
        self.assertIn('Poincaré, Henri', bib)

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex(self, reqget):
        bib = isbn2bibtex('9782081336742')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Poincaré, Henri')
        self.assertEqual(entry['title'], 'La science et l\'hypothèse')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_retrieve_fails_on_incorrect_ISBN(self, reqget):
        bib = isbn2bibtex('9' * 13)
        with self.assertRaises(EnDecoder.BibDecodingError):
            self.endecoder.decode_bibdata(bib)


class TestArxiv2Bibtex(APITests):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_new_style(self, reqget):
        bib = arxiv2bibtex('astro-ph/9812133')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Perlmutter, S.')
        self.assertEqual(entry['year'], '1999')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex_with_doi(self, reqget):
        bib = arxiv2bibtex('astro-ph/9812133')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Perlmutter, S.')
        self.assertEqual(entry['year'], '1999')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex_without_doi(self, reqget):
        bib = arxiv2bibtex('math/0211159')
        b = self.endecoder.decode_bibdata(bib)
        self.assertEqual(len(b), 1)
        entry = b[list(b)[0]]
        self.assertEqual(entry['author'][0], 'Perelman, Grisha')
        self.assertEqual(entry['year'], '2002')
        self.assertEqual(
                entry['title'],
                'The entropy formula for the Ricci flow and its geometric applications')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_wrong_id(self, reqget):
        with self.assertRaises(ReferenceNotFoundError):
            bib = arxiv2bibtex('INVALIDID')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_wrong_doi(self, reqget):
        bib = arxiv2bibtex('1312.2021')
        b = self.endecoder.decode_bibdata(bib)
        entry = b[list(b)[0]]
        self.assertEqual(entry['arxiv_doi'], '10.1103/INVALIDDOI.89.084044')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_good_doi(self, reqget):
        """Get the DOI bibtex instead of the arXiv one if possible"""
        bib = arxiv2bibtex('1710.08557')
        b = self.endecoder.decode_bibdata(bib)
        entry = b[list(b)[0]]
        self.assertTrue(not 'arxiv_doi' in entry)
        self.assertEqual(entry['doi'], '10.1186/s12984-017-0305-3')
        self.assertEqual(entry['title'].lower(), 'on neuromechanical approaches for the study of biological and robotic grasp and manipulation')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_good_doi_force_arxiv(self, reqget):
        bib = arxiv2bibtex('1710.08557', try_doi=False)
        b = self.endecoder.decode_bibdata(bib)
        entry = b[list(b)[0]]
        self.assertEqual(entry['arxiv_doi'], '10.1186/s12984-017-0305-3')
        self.assertEqual(entry['title'].lower(), 'on neuromechanical approaches for the study of biological grasp and\nmanipulation')


class TestArxiv2BibtexLocal(unittest.TestCase):
    """Test arXiv 2 Bibtex connection; those tests don't require a connection"""

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
