# -*- coding: utf-8 -*-
import unittest
import os

import dotdot
import fake_env

from pubs import endecoder, pretty

from str_fixtures import bibtex_raw0

class TestPretty(unittest.TestCase):

    def test_oneliner(self):

        decoder = endecoder.EnDecoder()
        bibdata = decoder.decode_bibdata(bibtex_raw0)
        pretty.bib_oneliner(bibdata['Page99'])

if __name__ == '__main__':
    unittest.main()
