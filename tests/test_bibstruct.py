# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
        bibdata['author'] = ['Zôu\\@/ , John']
        key = bibstruct.generate_citekey(doe_bibentry)
        self.assertEqual(key, 'Zou2013')

    def test_simple(self):
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry)
        self.assertEqual(key, 'Doe2013')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry)
        self.assertEqual(key, 'Salinger1961')

    def test_no_modifier(self):
        template = '{author_last_name}{year}'
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'Doe2013')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'Salinger1961')

    def test_all_keys(self):
        template = '{author_last_name}-{year}-{first_word}'
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'Doe-2013-Nice')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'Salinger-1961-Franny')

    def test_l_modifier(self):
        template = '{author_last_name:l}{year:l}'
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'doe2013')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'salinger1961')

    def test_u_modifier(self):
        template = '{author_last_name:u}{year:u}'
        bibentry = copy.deepcopy(fixtures.doe_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'DOE2013')

        bibentry = copy.deepcopy(fixtures.franny_bibentry)
        key = bibstruct.generate_citekey(bibentry, template)
        self.assertEqual(key, 'SALINGER1961', template)


if __name__ == '__main__':
    unittest.main()
