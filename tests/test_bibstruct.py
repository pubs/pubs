# -*- coding: utf-8 -*-
import os
import unittest
import copy

import dotdot
from pubs import bibstruct

import fixtures


class TestGenerateCitekey(unittest.TestCase):

    def test_fails_on_empty_paper(self):
        with self.assertRaises(ValueError):
            bibstruct.generate_citekey(None)

    def test_escapes_chars(self):
        doe_bibentry = copy.deepcopy(fixtures.doe_bibentry)
        citekey, bibdata = bibstruct.get_entry(doe_bibentry)
        bibdata['author'] = [u'Zôu\\@/ , John']
        key = bibstruct.generate_citekey(doe_bibentry)
        self.assertEqual(key, 'Zou2013')

    def test_simple(self):
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry)
        self.assertEqual(key, 'Doe2013')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry)
        self.assertEqual(key, 'Salinger1961')


if __name__ == '__main__':
    unittest.main()
