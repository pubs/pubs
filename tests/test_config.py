# -*- coding: utf-8 -*-
import unittest

import testenv
from papers import configs
from papers.configs import config
from papers.p3 import configparser

class TestConfig(unittest.TestCase):

    def test_create_config(self):
        a = configs.Config()
        a.as_global()
        self.assertEqual(a, config())

    def test_config_content(self):
        a = configs.Config()
        a.as_global()
        self.assertEqual(config().papers_dir, configs.DFT_PAPERS_DIR)
        self.assertEqual(config().color, configs.str2bool(configs.DFT_COLOR))

    def test_set(self):
        a = configs.Config()
        a.as_global()
        config().color = 'no'
        self.assertEqual(config().color, False)
        # booleans type for new variables are memorized, but not saved.
        config().bla = True
        self.assertEqual(config().bla, True)

        with self.assertRaises(configparser.NoOptionError):
            config()._cfg.get(configs.MAIN_SECTION, '_section')

    def test_reload(self):

        a = configs.Config()
        a.as_global()
        a.color = False
        a.bla = 'foo'
        config.color = not configs.str2bool(configs.DFT_COLOR)
        self.assertEqual(config().color, not configs.str2bool(configs.DFT_COLOR))

        b = configs.Config()
        b.as_global()
        self.assertEqual(b, config())
        self.assertEqual(config().color, configs.str2bool(configs.DFT_COLOR))

    def test_exception(self):

        a = configs.Config()
        a.as_global()

        with self.assertRaises(configparser.NoOptionError):
            config().color2

        with self.assertRaises(configparser.NoSectionError):
            config(section = 'bla3').color