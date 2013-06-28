# -*- coding: utf-8 -*-
import unittest

import testenv
from papers.commands.tag_cmd import _parse_tags, _tag_groups

class TestCreateCitekey(unittest.TestCase):

    def test_tag_parsing(self):

        self.assertEqual(['+abc', '+def9'], _parse_tags( 'abc+def9'))
        self.assertEqual(['+abc', '-def9'], _parse_tags( 'abc-def9'))
        self.assertEqual(['-abc', '-def9'], _parse_tags('-abc-def9'))
        self.assertEqual(['+abc', '-def9'], _parse_tags('+abc-def9'))

        self.assertEqual(({'math', 'romance'}, {'war'}), _tag_groups(_parse_tags('-war+math+romance')))
        self.assertEqual(({'math', 'romance'}, {'war'}), _tag_groups(_parse_tags('+math+romance-war')))
        self.assertEqual(({'math', 'romance'}, {'war'}), _tag_groups(_parse_tags('math+romance-war')))
