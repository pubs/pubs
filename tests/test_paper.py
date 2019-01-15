# -*- coding: utf-8 -*-

import unittest

import dotdot
import fixtures
import str_fixtures
from pubs.paper import Paper
from pubs.endecoder import EnDecoder


class TestAttributes(unittest.TestCase):

    def setUp(self):
        self.p = Paper.from_bibentry(
            fixtures.page_bibentry,
            metadata=fixtures.page_metadata).deepcopy()

    def test_tags(self):
        self.assertEqual(self.p.tags, set(['search', 'network']))

    def test_add_tag(self):
        self.p.add_tag('algorithm')
        self.assertEqual(self.p.tags, set(['search', 'network', 'algorithm']))
        self.p.add_tag('algorithm')
        self.assertEqual(self.p.tags, set(['search', 'network', 'algorithm']))

    def test_set_tags(self):
        self.p.tags = ['algorithm']
        self.assertEqual(self.p.tags, set(['algorithm']))

    def test_remove_tags(self):
        self.p.remove_tag('network')
        self.assertEqual(self.p.tags, set(['search']))

    def test_mixed_tags(self):
        self.p.add_tag('algorithm')
        self.assertEqual(self.p.tags, set(['search', 'network', 'algorithm']))
        self.p.remove_tag('network')
        self.assertEqual(self.p.tags, set(['search', 'algorithm']))
        self.p.tags = ['ranking']
        self.assertEqual(self.p.tags, set(['ranking']))
        self.p.remove_tag('ranking')
        self.assertEqual(self.p.tags, set())
        self.p.remove_tag('ranking')

    def test_fails_with_empty_citekey(self):
        with self.assertRaises(ValueError):
            Paper(" ", fixtures.doe_bibdata)


class TestPaperUnicodeBibdata(unittest.TestCase):

    def test_no_latex(self):
        p = Paper.from_bibentry(fixtures.page_bibentry,
                                metadata=fixtures.page_metadata).deepcopy()
        self.assertEqual(p.bibdata, p.get_unicode_bibdata())

    def test_latex_converted(self):
        bib = EnDecoder().decode_bibdata(str_fixtures.bibtex_with_latex)
        p = Paper.from_bibentry(bib)
        ubib = p.get_unicode_bibdata()
        self.assertEqual(ubib['author'][0], "Kjær, Kurt H")
        self.assertEqual(ubib['author'][3], "Bjørk, Anders A")


if __name__ == '__main__':
    unittest.main()
