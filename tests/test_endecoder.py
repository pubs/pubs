from __future__ import unicode_literals

import unittest

import yaml

import dotdot
from pubs import endecoder
from pubs.p3 import ustr

from fixtures import dummy_metadata
from str_fixtures import bibtex_raw0, metadata_raw0, turing_bib, bibtex_month


def compare_yaml_str(s1, s2):
    if s1 == s2:
        return True
    else:
        y1 = yaml.safe_load(s1)
        y2 = yaml.safe_load(s2)
        return y1 == y2


class TestEnDecode(unittest.TestCase):

    def test_decode_emptystring(self):
        decoder = endecoder.EnDecoder()
        with self.assertRaises(decoder.BibDecodingError):
            decoder.decode_bibdata('')

    def test_encode_bibtex_is_unicode(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)
        bibraw = decoder.encode_bibdata(entry)
        self.assertIsInstance(bibraw, ustr)

    def test_encode_metadat_is_unicode(self):
        decoder = endecoder.EnDecoder()
        data = decoder.encode_metadata(dummy_metadata)
        self.assertIsInstance(data, ustr)

    def test_endecode_bibtex(self):
        """Test that multiple encode/decode step preserve data"""
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

    def test_decode_bibtex_preserves_type_field(self):
        """Test that multiple encode/decode step preserve data"""
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)
        self.assertEqual(entry['Page99']['type'], "technical report")

    def test_endecode_bibtex_BOM(self):
        """Test that bibtexparser if fine with BOM-prefixed data"""
        decoder = endecoder.EnDecoder()
        bom_str = '\ufeff'

        entry_1  = decoder.decode_bibdata(bibtex_raw0)
        bibraw_1 = decoder.encode_bibdata(entry_1)
        entry_2  = decoder.decode_bibdata(bom_str + bibraw_1)
        bibraw_2 = decoder.encode_bibdata(entry_2)

        self.assertEqual(bibraw_1, bibraw_2)

    def test_endecode_bibtex_converts_month_string(self):
        """Test if `month=dec` is correctly recognized and transformed into
        `month={December}`"""
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_month)['Goyal2017']

        self.assertEqual(entry['month'], 'December')

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

    def test_endecode_keyword(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(turing_bib)
        keywords = ['artificial intelligence', 'Turing test']
        entry['turing1950computing']['keyword'] = keywords
        bibraw = decoder.encode_bibdata(entry)
        entry1 = decoder.decode_bibdata(bibraw)
        self.assertIn('keyword', entry1['turing1950computing'])
        self.assertEqual(set(keywords),
                         set(entry1['turing1950computing']['keyword']))

    def test_endecode_keyword_as_keywords(self):
        decoder = endecoder.EnDecoder()
        keywords = ['artificial intelligence', 'Turing test']
        # Add keywords to bibraw
        keyword_str = 'keywords = {artificial intelligence, Turing test},\n'
        biblines = turing_bib.splitlines()
        biblines.insert(-3, keyword_str)
        bibsrc = '\n'.join(biblines)
        entry = decoder.decode_bibdata(bibsrc)['turing1950computing']
        self.assertNotIn('keywords', entry)
        self.assertIn('keyword', entry)
        self.assertEqual(set(keywords), set(entry['keyword']))

    def test_decode_metadata(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_metadata(metadata_raw0)
        expected = {'docfile': 'docsdir://Page99.pdf',
                    'tags': ['search', 'network'],
                    'added': '2013-11-14 13:14:20',
                    }
        self.assertEqual(entry, expected)

    def test_endecode_metadata(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_metadata(metadata_raw0)
        metadata_output0 = decoder.encode_metadata(entry)
        entry_from_encode = decoder.decode_metadata(metadata_output0)
        self.assertEqual(entry, entry_from_encode)

    def test_endecode_bibtex_field_order(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)
        lines = decoder.encode_bibdata(entry).splitlines()
        self.assertEqual(lines[1].split('=')[0].strip(), 'author')
        self.assertEqual(lines[2].split('=')[0].strip(), 'title')
        self.assertEqual(lines[3].split('=')[0].strip(), 'institution')
        self.assertEqual(lines[4].split('=')[0].strip(), 'publisher')
        self.assertEqual(lines[5].split('=')[0].strip(), 'year')
        self.assertEqual(lines[6].split('=')[0].strip(), 'month')
        self.assertEqual(lines[7].split('=')[0].strip(), 'number')
        self.assertEqual(lines[8].split('=')[0].strip(), 'url')
        self.assertEqual(lines[9].split('=')[0].strip(), 'note')
        self.assertEqual(lines[10].split('=')[0].strip(), 'abstract')

    def test_endecode_link_as_url(self):
        decoder = endecoder.EnDecoder()
        if 'url = ' not in bibtex_raw0:
            raise NotImplementedError(
                'The fixture bibraw0 has been changed; test needs an update.')
        raw_with_link = bibtex_raw0.replace('url = ', 'link = ')
        entry = decoder.decode_bibdata(raw_with_link)
        lines = decoder.encode_bibdata(entry).splitlines()
        self.assertEqual(lines[8].split('=')[0].strip(), 'url')
        self.assertEqual(lines[8].split('=')[1].strip(),
                         '{http://ilpubs.stanford.edu:8090/422/},')

    def test_endecode_bibtex_ignores_fields(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)

        bibraw1 = decoder.encode_bibdata(
            entry, ignore_fields=['title', 'note', 'abstract', 'journal'])
        entry1 = list(decoder.decode_bibdata(bibraw1).values())[0]

        self.assertNotIn('title', entry1)
        self.assertNotIn('note', entry1)
        self.assertNotIn('abtract', entry1)
        self.assertIn('author', entry1)
        self.assertIn('institution', entry1)

    def test_endecodes_raises_exception(self):
        decoder = endecoder.EnDecoder()
        with self.assertRaises(decoder.BibDecodingError):
            decoder.decode_bibdata("@misc{I am not a correct bibtex{{}")

    def test_endecode_preserves_type(self):
        decoder = endecoder.EnDecoder()
        entry = decoder.decode_bibdata(bibtex_raw0)

        bibraw1 = decoder.encode_bibdata(
            entry, ignore_fields=['title', 'note', 'abstract', 'journal'])



if __name__ == '__main__':
    unittest.main()
