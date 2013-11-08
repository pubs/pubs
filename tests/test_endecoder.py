# -*- coding: utf-8 -*-
import unittest

import yaml

import testenv
from papers import endecoder

from str_fixtures import bibyaml_raw0, bibtexml_raw0, bibtex_raw0, metadata_raw0

def compare_yaml_str(s1, s2):
    if s1 == s2:
        return True
    else:
        y1 = yaml.safe_load(s1)
        y2 = yaml.safe_load(s2)
        return y1 == y2


class TestEnDecode(unittest.TestCase):

    def test_endecode_bibyaml(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibyaml_raw0)
        bibyaml_output0 = decoder.encode_bibdata(entry)

        self.assertEqual(bibyaml_raw0, bibyaml_output0)
        self.assertTrue(compare_yaml_str(bibyaml_raw0, bibyaml_output0))

    def test_endecode_bibtexml(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtexml_raw0)
        bibyaml_output0 = decoder.encode_bibdata(entry)

        self.assertTrue(compare_yaml_str(bibyaml_raw0, bibyaml_output0))
        
    def test_endecode_bibtex(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)
        bibyaml_output0 = decoder.encode_bibdata(entry)

        self.assertTrue(compare_yaml_str(bibyaml_raw0, bibyaml_output0))

    def test_endecode_metadata(self):

        decoder = endecoder.EnDecoder()
        entry = decoder.decode_metadata(metadata_raw0)
        metadata_output0 = decoder.encode_metadata(entry)

        self.assertEqual(metadata_raw0, metadata_output0)

