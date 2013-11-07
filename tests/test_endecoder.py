# -*- coding: utf-8 -*-
import unittest

import yaml

import testenv
from papers import endecoder

bibyaml_raw0 = """entries:
    Page99:
        abstract: The importance of a Web page is an inherently subjective matter,
            which depends on the readers interests, knowledge and attitudes. But there
            is still much that can be said objectively about the relative importance
            of Web pages. This paper describes PageRank, a mathod for rating Web pages
            objectively and mechanically, effectively measuring the human interest
            and attention devoted to them. We compare PageRank to an idealized random
            Web surfer. We show how to efficiently compute PageRank for large numbers
            of pages. And, we show how to apply PageRank to search and to user navigation.
        author:
        -   first: Lawrence
            last: Page
        -   first: Sergey
            last: Brin
        -   first: Rajeev
            last: Motwani
        -   first: Terry
            last: Winograd
        institution: Stanford InfoLab
        month: November
        note: Previous number = SIDL-WP-1999-0120
        number: 1999-66
        publisher: Stanford InfoLab
        title: 'The PageRank Citation Ranking: Bringing Order to the Web.'
        type: techreport
        url: http://ilpubs.stanford.edu:8090/422/
        year: '1999'
"""

bibtexml_raw0 = """<?xml version='1.0' encoding='UTF-8'?>
<bibtex:file xmlns:bibtex="http://bibtexml.sf.net/">

    <bibtex:entry id="Page99">
        <bibtex:techreport>
            <bibtex:publisher>Stanford InfoLab</bibtex:publisher>
            <bibtex:title>The PageRank Citation Ranking: Bringing Order to the Web.</bibtex:title>
            <bibtex:url>http://ilpubs.stanford.edu:8090/422/</bibtex:url>
            <bibtex:abstract>The importance of a Web page is an inherently subjective matter, which depends on the readers interests, knowledge and attitudes. But there is still much that can be said objectively about the relative importance of Web pages. This paper describes PageRank, a mathod for rating Web pages objectively and mechanically, effectively measuring the human interest and attention devoted to them. We compare PageRank to an idealized random Web surfer. We show how to efficiently compute PageRank for large numbers of pages. And, we show how to apply PageRank to search and to user navigation.</bibtex:abstract>
            <bibtex:number>1999-66</bibtex:number>
            <bibtex:month>November</bibtex:month>
            <bibtex:note>Previous number = SIDL-WP-1999-0120</bibtex:note>
            <bibtex:year>1999</bibtex:year>
            <bibtex:institution>Stanford InfoLab</bibtex:institution>
            <bibtex:author>
                <bibtex:person>
                    <bibtex:first>Lawrence</bibtex:first>
                    <bibtex:last>Page</bibtex:last>
                </bibtex:person>
                <bibtex:person>
                    <bibtex:first>Sergey</bibtex:first>
                    <bibtex:last>Brin</bibtex:last>
                </bibtex:person>
                <bibtex:person>
                    <bibtex:first>Rajeev</bibtex:first>
                    <bibtex:last>Motwani</bibtex:last>
                </bibtex:person>
                <bibtex:person>
                    <bibtex:first>Terry</bibtex:first>
                    <bibtex:last>Winograd</bibtex:last>
                </bibtex:person>
            </bibtex:author>
        </bibtex:techreport>
    </bibtex:entry>

</bibtex:file>
"""

bibtex_raw0 = """
@techreport{
    Page99,
    author = "Page, Lawrence and Brin, Sergey and Motwani, Rajeev and Winograd, Terry",
    publisher = "Stanford InfoLab",
    title = "The PageRank Citation Ranking: Bringing Order to the Web.",
    url = "http://ilpubs.stanford.edu:8090/422/",
    abstract = "The importance of a Web page is an inherently subjective matter, which depends on the readers interests, knowledge and attitudes. But there is still much that can be said objectively about the relative importance of Web pages. This paper describes PageRank, a mathod for rating Web pages objectively and mechanically, effectively measuring the human interest and attention devoted to them. We compare PageRank to an idealized random Web surfer. We show how to efficiently compute PageRank for large numbers of pages. And, we show how to apply PageRank to search and to user navigation.",
    number = "1999-66",
    month = "November",
    note = "Previous number = SIDL-WP-1999-0120",
    year = "1999",
    institution = "Stanford InfoLab"
}
"""

metadata_raw0 = """external-document: null
notes: []
tags: [search, network]
"""

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

