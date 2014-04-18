# -*- coding: utf-8 -*-
import unittest

import yaml

import dotdot
from pubs import endecoder

from str_fixtures import bibtex_raw0, metadata_raw0, turing_bib

def compare_yaml_str(s1, s2):
    if s1 == s2:
        return True
    else:
        y1 = yaml.safe_load(s1)
        y2 = yaml.safe_load(s2)
        return y1 == y2


class TestEnDecode(unittest.TestCase):

    def test_endecode_bibtex(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)

        bibraw1 = decoder.encode_bibdata(entry)
        entry1  = decoder.decode_bibdata(bibraw1)
        bibraw2 = decoder.encode_bibdata(entry1)
        entry2  = decoder.decode_bibdata(bibraw2)

        for citekey in entry1.keys():
            bibentry1 = entry1[citekey]
            bibentry2 = entry2[citekey]
            for key, value in bibentry1.items():
                self.assertEqual(bibentry1[key], bibentry2[key])

        self.assertEqual(bibraw1, bibraw2)

    def test_endecode_bibtex_editor(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(turing_bib)

        bibraw1 = decoder.encode_bibdata(entry)
        entry1  = decoder.decode_bibdata(bibraw1)
        bibraw2 = decoder.encode_bibdata(entry1)
        entry2  = decoder.decode_bibdata(bibraw2)

        for citekey in entry1.keys():
            bibentry1 = entry1[citekey]
            bibentry2 = entry2[citekey]
            for key, value in bibentry1.items():
                self.assertEqual(bibentry1[key], bibentry2[key])

        self.assertEqual(bibraw1, bibraw2)

    def test_endecode_metadata(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_metadata(metadata_raw0)
        metadata_output0 = decoder.encode_metadata(entry)

        self.assertEqual(set(metadata_raw0.split('\n')), set(metadata_output0.split('\n')))


if __name__ == '__main__':
    unittest.main()
