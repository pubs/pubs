# coding: utf8

from __future__ import unicode_literals
import unittest

from pubs.utils import standardize_doi


class TestDOIStandardization(unittest.TestCase):

    def setUp(self):
        # some of these come from
        # https://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
        self.crossref_dois = (
            '10.2310/JIM.0b013e31820bab4c',
            '10.1007/978-3-642-28108-2_19',
            '10.1016/S0735-1097(98)00347-7',
        )

        self.hard_dois = (
            '10.1175/1520-0485(2002)032<0870:CT>2.0.CO;2',
            '10.1002/(SICI)1522-2594(199911)42:5<952::AID-MRM16>3.0.CO;2-S',
            '10.1579/0044-7447(2006)35[89:RDUICP]2.0.CO;2',
        )

        self.currently_not_supported = (
            '10.1007.10/978-3-642-28108-2_19',
            '10.1000.10/123456',
            '10.1016.12.31/nature.S0735-1097(98)2000/12/31/34:7-7',
        )

    def test_http_dxdoi_org(self):
        doi = 'http://dx.doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_https_dxdoi_org(self):
        doi = 'https://dx.doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_http_doi_org(self):
        doi = 'http://doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_https_doi_org(self):
        doi = 'https://doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_doi_org(self):
        doi = 'doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_dxdoi_org(self):
        doi = 'dx.doi.org/10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_doi_colon(self):
        doi = 'doi:10.1109/5.771073'
        sdoi = standardize_doi(doi)
        self.assertEqual(sdoi, '10.1109/5.771073')

    def test_crossref_dois(self):
        for doi in self.crossref_dois:
            sdoi = standardize_doi(doi)
            self.assertEqual(doi, sdoi)

    def test_hard_dois(self):
        for doi in self.hard_dois:
            sdoi = standardize_doi(doi)
            self.assertEqual(doi, sdoi)

    def test_currently_not_supported(self):
        for doi in self.currently_not_supported:
            with self.assertRaises(ValueError):
                standardize_doi(doi)


if __name__ == '__main__':
    unittest.main()
