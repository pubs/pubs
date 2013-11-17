# -*- coding: utf-8 -*-
import os
import unittest
import copy

from pybtex.database import Person

import testenv
from pubs import bibstruct

import fixtures


class TestGenerateCitekey(unittest.TestCase):

    def test_escapes_chars(self):
        doe_bibdata = copy.deepcopy(fixtures.doe_bibdata)
        citekey, entry = bibstruct.get_entry(doe_bibdata)
        entry.persons['author'] = [Person(string=u'Zôu\\@/ , John')]
        key = bibstruct.generate_citekey(doe_bibdata)

    def test_simple(self):
        bibdata = copy.deepcopy(fixtures.doe_bibdata)
        key = bibstruct.generate_citekey(bibdata)
        self.assertEqual(key, 'Doe2013')

        bibdata = copy.deepcopy(fixtures.franny_bibdata)
        key = bibstruct.generate_citekey(bibdata)
        self.assertEqual(key, 'Salinger1961')
