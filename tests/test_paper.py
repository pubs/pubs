# -*- coding: utf-8 -*-
import os
import unittest

import testenv
import fixtures
from pubs.paper import Paper


class TestAttributes(unittest.TestCase):

    def test_tags(self):
        p = Paper(fixtures.page_bibdata, metadata=fixtures.page_metadata)
        self.assertEqual(p.tags, set(['search', 'network']))


