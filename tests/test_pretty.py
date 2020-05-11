from __future__ import unicode_literals

import unittest

import dotdot

from pubs import endecoder, pretty, color, config

from str_fixtures import bibtex_raw0


class TestPretty(unittest.TestCase):

    def setUp(self):
        conf = config.load_default_conf()
        color.setup(conf)

    def test_oneliner(self):
        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        line = 'Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999)'
        self.assertEqual(color.undye(pretty.bib_oneliner(bibdata['Page99'])), line)

    def test_oneliner_no_year(self):
        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        bibdata['Page99'].pop('year')
        line = 'Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web."'
        self.assertEqual(color.undye(pretty.bib_oneliner(bibdata['Page99'])), line)

    def test_oneliner_max_authors(self):
        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        for max_authors in [1, 2, 3]:
            line = 'Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999)'
            self.assertEqual(color.undye(pretty.bib_oneliner(bibdata['Page99'], max_authors=max_authors)), line)
        for max_authors in [-1, 0, 4, 5, 10]:
            line = 'Page, Lawrence and Brin, Sergey and Motwani, Rajeev and Winograd, Terry "The PageRank Citation Ranking: Bringing Order to the Web." (1999)'
            self.assertEqual(color.undye(pretty.bib_oneliner(bibdata['Page99'], max_authors=max_authors)), line)

if __name__ == '__main__':
    unittest.main()
