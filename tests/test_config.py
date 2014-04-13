# -*- coding: utf-8 -*-
import unittest

import dotdot
from pubs import configs
from pubs.configs import config
from pubs.p3 import configparser

class TestConfig(unittest.TestCase):

    def test_create_config(self):
        a = configs.Config()
        a.as_global()
        self.assertEqual(a, config())

    def test_config_content(self):
        a = configs.Config()
        a.as_global()

        self.assertEqual(config().pubsdir, configs.DFT_CONFIG['pubsdir'])
        self.assertEqual(config().color, configs.str2bool(configs.DFT_CONFIG['color']))

    def test_set(self):
        a = configs.Config()
        a.as_global()
        config().color = 'no'
        self.assertEqual(config().color, False)
        self.assertEqual(config('pubs').color, False)
        # booleans type for new variables are memorized, but not saved.
        config().bla = True
        self.assertEqual(config().bla, True)
        self.assertEqual(config('pubs').bla, True)

        with self.assertRaises(configparser.NoOptionError):
            config()._cfg.get(configs.MAIN_SECTION, '_section')

    def test_reload(self):

        default_color = configs.DFT_CONFIG['color']

        a = configs.Config()
        a.as_global()
        a.color = False
        a.bla = 'foo'
        config.color = not configs.str2bool(default_color)
        self.assertEqual(config().color, not configs.str2bool(default_color))

        b = configs.Config()
        b.as_global()
        self.assertEqual(b, config())
        self.assertEqual(config().color, configs.str2bool(default_color))

    def test_exception(self):

        a = configs.Config()
        a.as_global()

        with self.assertRaises(configparser.NoOptionError):
            config().color2
        self.assertEqual(config().get('color2', default = 'blue'), 'blue')

        with self.assertRaises(configparser.NoSectionError):
            config(section = 'bla3').color
        self.assertEqual(config(section = 'bla3').get('color', default = 'green'), 'green')
        self.assertEqual(config(section = 'bla3').get('color', default = config().color), True)

    def test_keywords(self):
        a = configs.Config(pubs_dir = '/blabla')
        self.assertEqual(a.pubs_dir, '/blabla')


if __name__ == '__main__':
    unittest.main()
