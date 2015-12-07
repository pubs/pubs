# -*- coding: utf-8 -*-
import unittest

import dotdot
from pubs.commands.tag_cmd import _parse_tag_seq, _tag_groups

class TestTag(unittest.TestCase):

    def test_parse_tags(self):
        self.assertEqual(['+abc', '+def9'], _parse_tag_seq('abc+def9'))
        self.assertEqual(['+abc', '-def9'], _parse_tag_seq('abc-def9'))
        self.assertEqual(['-abc', '-def9'], _parse_tag_seq('-abc-def9'))
        self.assertEqual(['+abc', '-def9'], _parse_tag_seq('+abc-def9'))

    def test_tag_groups(self):
        self.assertEqual(({'math', 'romance'}, {'war'}),
                         _tag_groups(_parse_tag_seq('-war+math+romance')))
        self.assertEqual(({'math', 'romance'}, {'war'}),
                         _tag_groups(_parse_tag_seq(':war+math+romance')))
        self.assertEqual(({'math', 'romance'}, {'war'}),
                         _tag_groups(_parse_tag_seq('+math+romance-war')))
        self.assertEqual(({'math', 'romance'}, {'war'}),
                         _tag_groups(_parse_tag_seq('math+romance-war')))


if __name__ == '__main__':
    unittest.main()
