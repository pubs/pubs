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
        doe_bibdata = copy.deepcopy(fixtures.doe_bibdata)
        citekey, entry = bibstruct.get_entry(doe_bibdata)
        entry['author'] = [u'Zôu\\@/ , John']
        key = bibstruct.generate_citekey(doe_bibdata)

    def test_simple(self):
        bibdata = copy.deepcopy(fixtures.doe_bibdata)
        key = bibstruct.generate_citekey(bibdata)
        self.assertEqual(key, 'Doe2013')

        bibdata = copy.deepcopy(fixtures.franny_bibdata)
        key = bibstruct.generate_citekey(bibdata)
        self.assertEqual(key, 'Salinger1961')


if __name__ == '__main__':
    unittest.main()
