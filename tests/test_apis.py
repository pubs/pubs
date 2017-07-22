# coding: utf8

from __future__ import unicode_literals
import unittest

import dotdot

from pubs.p3 import ustr
from pubs.endecoder import EnDecoder
from pubs.apis import doi2bibtex, isbn2bibtex


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

    def test_parse_fails_on_incorrect_DOI(self):
        bib = doi2bibtex('999999')
        with self.assertRaises(ValueError):
            self.endecoder.decode_bibdata(bib)


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

    def test_parse_fails_on_incorrect_ISBN(self):
        bib = doi2bibtex('9' * 13)
        with self.assertRaises(ValueError):
            self.endecoder.decode_bibdata(bib)


# Note: apparently ottobib.com uses caracter modifiers for accents instead
# of the correct unicode characters. TODO: Should we convert them?
