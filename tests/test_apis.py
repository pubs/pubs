# coding: utf8

from __future__ import unicode_literals
import unittest

import mock
import pytest

import dotdot

from pubs.p3 import ustr
from pubs import apis
from pubs.apis import _is_arxiv_oldstyle, _extract_arxiv_id

import mock_requests


class APITests(unittest.TestCase):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_readme(self, reqget):
        apis.doi2bibtex('10.1007/s00422-012-0514-6')
        # apis.isbn2bibtex('978-0822324669')  # FIXME: uncomment when ISBNs work again
        apis.arxiv2bibtex('math/9501234')

class TestDOI2Bibtex(APITests):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_unicode(self, reqget):
        bib = apis.doi2bibtex('10.1007/BF01700692')
        self.assertIsInstance(bib, ustr)
        self.assertIn('Kurt Gödel', bib)

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex(self, reqget):
        bib = apis.get_bibentry_from_api('10.1007/BF01700692', 'DOI')
        self.assertEqual(len(bib), 1)
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['author'][0], 'Gödel, Kurt')
        self.assertEqual(entry['title'],
                         'Über formal unentscheidbare Sätze der Principia '
                         'Mathematica und verwandter Systeme I')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_retrieve_fails_on_incorrect_DOI(self, reqget):
        with self.assertRaises(apis.ReferenceNotFoundError):
            apis.get_bibentry_from_api('999999', 'doi')


class TestISBN2Bibtex(APITests):

    # try to avoid triggering 403 status during tests.
    # @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    # def test_unicode(self, reqget):
    #     bib = apis.isbn2bibtex('9782081336742')
    #     self.assertIsInstance(bib, ustr)
    #     self.assertIn('Poincaré, Henri', bib)

    @pytest.mark.skip(reason="isbn is not working anymore, see https://github.com/pubs/pubs/issues/276")
    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex(self, reqget):
        bib = apis.get_bibentry_from_api('9782081336742', 'ISBN')
        self.assertEqual(len(bib), 1)
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['author'][0], 'Poincaré, Henri')
        self.assertEqual(entry['title'], 'La science et l\'hypothèse')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_retrieve_fails_on_incorrect_ISBN(self, reqget):
        with self.assertRaises(apis.ReferenceNotFoundError):
            apis.get_bibentry_from_api('9' * 13, 'isbn')


class TestArxiv2Bibtex(APITests):

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_new_style(self, reqget):
        bib = apis.get_bibentry_from_api('astro-ph/9812133', 'arXiv')
        self.assertEqual(len(bib), 1)
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['author'][0], 'Perlmutter, S.')
        self.assertEqual(entry['year'], '1999')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex_with_doi(self, reqget):
        bib = apis.get_bibentry_from_api('astro-ph/9812133', 'arxiv')
        self.assertEqual(len(bib), 1)
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['author'][0], 'Perlmutter, S.')
        self.assertEqual(entry['year'], '1999')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_parses_to_bibtex_without_doi(self, reqget):
        bib = apis.get_bibentry_from_api('math/0211159', 'ARXIV')
        self.assertEqual(len(bib), 1)
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['author'][0], 'Perelman, Grisha')
        self.assertEqual(entry['year'], '2002')
        self.assertEqual(
                entry['title'],
                'The entropy formula for the Ricci flow and its geometric applications')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_wrong_id(self, reqget):
        with self.assertRaises(apis.ReferenceNotFoundError):
            bib = apis.get_bibentry_from_api('INVALIDID', 'arxiv')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_wrong_doi(self, reqget):
        bib = apis.get_bibentry_from_api('1312.2021', 'arXiv')
        entry = bib[list(bib)[0]]
        self.assertEqual(entry['arxiv_doi'], '10.1103/INVALIDDOI.89.084044')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_good_doi(self, reqget):
        """Get the DOI bibtex instead of the arXiv one if possible"""
        bib = apis.get_bibentry_from_api('1710.08557', 'arXiv')
        entry = bib[list(bib)[0]]
        self.assertTrue(not 'arxiv_doi' in entry)
        self.assertEqual(entry['doi'], '10.1186/s12984-017-0305-3')
        self.assertEqual(entry['title'].lower(), 'on neuromechanical approaches for the study of biological and robotic grasp and manipulation')

    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_arxiv_good_doi_force_arxiv(self, reqget):
        bib = apis.get_bibentry_from_api('1710.08557', 'arXiv', try_doi=False)
        entry = bib[list(bib)[0]]
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
