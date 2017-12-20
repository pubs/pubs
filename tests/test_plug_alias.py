import shlex
import unittest

import dotdot

import pubs
from pubs import config
from pubs.plugs.alias.alias import (Alias, AliasPlugin, CommandAlias,
                                    ShellAlias)


def to_args(arg_strings):
    o = lambda: None  # Dirty hack
    o.prog = 'pubs'
    o.arguments = arg_strings
    return o


class FakeExecuter(object):

    called = None
    executed = None

    def call(self, obj, shell=None):
        self.called = obj

    def execute(self, obj):
        self.executed = obj


class AliasTestCase(unittest.TestCase):

    def setUp(self):
        self.subprocess = FakeExecuter()
        pubs.plugs.alias.alias.subprocess = self.subprocess
        self.cmd_execute = FakeExecuter()
        pubs.plugs.alias.alias.execute = self.cmd_execute.execute

    def testAlias(self):
        alias = Alias.create_alias('print', 'open -w lpppp')
        alias.command(None, to_args(['CiteKey']))
        self.assertIsNone(self.subprocess.called)
        self.assertEqual(self.cmd_execute.executed,
                         ['pubs', 'open', '-w', 'lpppp', 'CiteKey'])

    def testShellAlias(self):
        """This actually just test that subprocess.call is called.
        """
        alias = Alias.create_alias('count', '!pubs list -k | wc -l')
        alias.command(None, to_args([]))
        self.assertIsNone(self.cmd_execute.executed)
        self.assertIsNotNone(self.subprocess.called)

    def testShellAliasEscapes(self):
        alias = Alias.create_alias('count', '!echo "$@"')
        args = ['a b c', "d,e f\""]
        alias.command(None, to_args(args))
        self.assertIsNone(self.cmd_execute.executed)
        self.assertIsNotNone(self.subprocess.called)
        self.assertEqual(
            shlex.split(self.subprocess.called.splitlines()[-1])[1:],
            args)


class AliasPluginTestCase(unittest.TestCase):

    def setUp(self):
        self.conf = config.load_default_conf()
        self.conf['plugins']['active'] = ['alias']

    def testAliasPluginCreated(self):
        self.plugin = AliasPlugin(self.conf)

    def testAliasPluginOneCommnand(self):
        self.conf['plugins']['alias'] = {'print': 'open -w lpppp'}
        self.plugin = AliasPlugin(self.conf)
        self.assertEqual(len(self.plugin.aliases), 1)
        self.assertEqual(type(self.plugin.aliases[0]), CommandAlias)
        self.assertEqual(self.plugin.aliases[0].name, 'print')
        self.assertEqual(self.plugin.aliases[0].definition, 'open -w lpppp')

    def testAliasPluginOneShell(self):
        self.conf['plugins']['alias'] = {'count': '!pubs list -k | wc -l'}
        self.plugin = AliasPlugin(self.conf)
        self.assertEqual(len(self.plugin.aliases), 1)
        self.assertEqual(type(self.plugin.aliases[0]), ShellAlias)
        self.assertEqual(self.plugin.aliases[0].name, 'count')
        self.assertEqual(self.plugin.aliases[0].definition,
                         'pubs list -k | wc -l')

    def testAliasPluginTwoCommnands(self):
        self.conf['plugins']['alias'] = {'print': 'open -w lpppp',
                                         'count': '!pubs list -k | wc -l'}
        self.plugin = AliasPlugin(self.conf)
        self.assertEqual(len(self.plugin.aliases), 2)

    def testAliasPluginNestedDefinitionType(self):
        self.conf['plugins']['alias'] = {'print': {'description': 'print this',
                                                   'command': 'open -w lpppp'}}
        self.plugin = AliasPlugin(self.conf)
        self.assertEqual(len(self.plugin.aliases), 1)
        self.assertEqual(type(self.plugin.aliases[0]), CommandAlias)
        self.assertEqual(self.plugin.aliases[0].name, 'print')
        self.assertEqual(self.plugin.aliases[0].description, 'print this')
        self.assertEqual(self.plugin.aliases[0].definition, 'open -w lpppp')

    def testAliasPluginMixedDefinitionTypes(self):
        self.conf['plugins']['alias'] = {'print': {'description': 'print this',
                                                   'command': 'open -w lpppp'},
                                         'count': '!pubs list -k | wc -l'}
        self.plugin = AliasPlugin(self.conf)
        self.plugin.aliases = sorted(self.plugin.aliases, key=lambda a: a.name)

        self.assertEqual(len(self.plugin.aliases), 2)
        self.assertEqual(type(self.plugin.aliases[1]), CommandAlias)
        self.assertEqual(type(self.plugin.aliases[0]), ShellAlias)

        self.assertEqual(self.plugin.aliases[0].name, 'count')
        self.assertEqual(self.plugin.aliases[0].description,
                         'user alias for `pubs list -k | wc -l`')
        self.assertEqual(self.plugin.aliases[0].definition,
                         'pubs list -k | wc -l')

        self.assertEqual(self.plugin.aliases[1].name, 'print')
        self.assertEqual(self.plugin.aliases[1].description, 'print this')
        self.assertEqual(self.plugin.aliases[1].definition, 'open -w lpppp')

    def testAliasPluginWrongDefinitionOrder(self):
        self.conf['plugins']['alias'] = {'print': {'description': 'print this',
                                                   'command': 'open -w lpppp',
                                         'count': '!pubs list -k | wc -l'}}
        self.plugin = AliasPlugin(self.conf)

        self.assertEqual(len(self.plugin.aliases), 1)
        self.assertEqual(type(self.plugin.aliases[0]), CommandAlias)

        self.assertEqual(self.plugin.aliases[0].name, 'print')
        self.assertEqual(self.plugin.aliases[0].description, 'print this')
        self.assertEqual(self.plugin.aliases[0].definition, 'open -w lpppp')
