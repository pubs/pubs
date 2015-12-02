# -*- coding: utf-8 -*-
import unittest
import os

import dotdot
import fake_env

from pubs import endecoder, pretty, color

from str_fixtures import bibtex_raw0


class TestPretty(unittest.TestCase):

    def setUp(self):
        color.setup()

    def test_oneliner(self):
        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        line = u'Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999)'
        self.assertEqual(pretty.bib_oneliner(bibdata['Page99']), line)

    def test_oneliner_no_year(self):
        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        bibdata['Page99'].pop('year')
        line = u'Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web."'
        self.assertEqual(pretty.bib_oneliner(bibdata['Page99']), line)

if __name__ == '__main__':
    unittest.main()
