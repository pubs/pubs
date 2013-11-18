# -*- coding: utf-8 -*-
import os
import unittest

import testenv
import fixtures
from pubs.paper import Paper


class TestAttributes(unittest.TestCase):

    def test_tags(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata).deepcopy()
        self.assertEqual(p.tags, set(['search', 'network']))

    def test_add_tag(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata).deepcopy()
        p.add_tag('algorithm')
        self.assertEqual(p.tags, set(['search', 'network', 'algorithm']))
        p.add_tag('algorithm')
        self.assertEqual(p.tags, set(['search', 'network', 'algorithm']))

    def test_set_tags(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata).deepcopy()
        p.tags = ['algorithm']
        self.assertEqual(p.tags, set(['algorithm']))

    def test_remove_tags(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata).deepcopy()
        p.remove_tag('network')
        self.assertEqual(p.tags, set(['search']))

    def test_mixed_tags(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata).deepcopy()
        p.add_tag('algorithm')
        self.assertEqual(p.tags, set(['search', 'network', 'algorithm']))
        p.remove_tag('network')
        self.assertEqual(p.tags, set(['search', 'algorithm']))
        p.tags = ['ranking']
        self.assertEqual(p.tags, set(['ranking']))
        p.remove_tag('ranking')
        self.assertEqual(p.tags, set())
        p.remove_tag('ranking')
