import unittest
import re
import os

import dotdot
import fake_env

from pubs import pubs_cmd
from pubs import color, content, filebroker, uis, beets_ui, p3, endecoder

import str_fixtures
import fixtures


from pubs.commands import init_cmd, import_cmd

    # code for fake fs

class TestFakeInput(unittest.TestCase):

    def test_input(self):
        input = fake_env.FakeInput(['yes', 'no'])
        self.assertEqual(input(), 'yes')
        self.assertEqual(input(), 'no')
        with self.assertRaises(IndexError):
            input()

    def test_input2(self):
        other_input = fake_env.FakeInput(['yes', 'no'], module_list=[color])
        other_input.as_global()
        self.assertEqual(color.input(), 'yes')
        self.assertEqual(color.input(), 'no')
        with self.assertRaises(IndexError):
            color.input()

    def test_editor_input(self):
        other_input = fake_env.FakeInput(['yes', 'no'],
                                         module_list=[content, color])
        other_input.as_global()
        self.assertEqual(content.editor_input(), 'yes')
        self.assertEqual(content.editor_input(), 'no')
        with self.assertRaises(IndexError):
            color.input()


class CommandTestCase(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    maxDiff = None

    def setUp(self):
        self.fs = fake_env.create_fake_fs([content, filebroker, init_cmd, import_cmd])

    def execute_cmds(self, cmds, fs=None, capture_output=True):
        """ Execute a list of commands, and capture their output

        A command can be a string, or a tuple of size 2 or 3.
        In the latter case, the command is :
        1. a string reprensenting the command to execute
        2. the user inputs to feed to the command during execution
        3. the output excpected, verified with assertEqual

        """
        outs = []
        for cmd in cmds:
            if hasattr(cmd, '__iter__'):
                if len(cmd) == 2:
                    input = fake_env.FakeInput(cmd[1], [content, uis, beets_ui, p3])
                    input.as_global()

                if capture_output:
                    _, stdout, stderr = fake_env.redirect(pubs_cmd.execute)(cmd[0].split())
                    if len(cmd) == 3 and capture_output:
                        actual_out  = color.undye(stdout.getvalue())
                        correct_out = color.undye(cmd[2])
                        self.assertEqual(actual_out, correct_out)
                else:
                    pubs_cmd.execute(cmd.split())

            else:
                if capture_output:
                    assert isinstance(cmd, str)
                    _, stdout, stderr = fake_env.redirect(pubs_cmd.execute)(cmd.split())
                else:
                    pubs_cmd.execute(cmd.split())

            if capture_output:
                assert(stderr.getvalue() == '')
                outs.append(color.undye(stdout.getvalue()))
        return outs

    def tearDown(self):
        fake_env.unset_fake_fs([content, filebroker])


class DataCommandTestCase(CommandTestCase):
    """Abstract TestCase intializing the fake filesystem and
    copying fake data.
    """

    def setUp(self):
        CommandTestCase.setUp(self)
        fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'data'), 'data')


# Actual tests

class TestInit(CommandTestCase):

    def test_init(self):
        pubsdir = os.path.expanduser('~/pubs_test2')
        pubs_cmd.execute('pubs init -p {}'.format(pubsdir).split())
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes'})

    def test_init2(self):
        pubsdir = os.path.expanduser('~/.pubs')
        pubs_cmd.execute('pubs init'.split())
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes'})


class TestAdd(DataCommandTestCase):

    def test_add(self):
        cmds = ['pubs init',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)

    def test_add2(self):
        cmds = ['pubs init -p /not_default',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(self.fs['os'].listdir('/not_default/doc')), {'Page99.pdf'})


class TestList(DataCommandTestCase):

    def test_list(self):
        cmds = ['pubs init -p /not_default2',
                'pubs list',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                'pubs list',
                ]
        self.execute_cmds(cmds)

    def test_list_smart_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list title:language author:Saunders',
                ]
        outs = self.execute_cmds(cmds)
        print outs[-1]
        self.assertEquals(1, len(outs[-1].split('/n')))

    def test_list_ignore_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --ignore-case title:lAnguAge author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEquals(1, len(outs[-1].split('/n')))

    def test_list_force_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --force-case title:Language author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEquals(0 + 1, len(outs[-1].split('/n')))



class TestUsecase(DataCommandTestCase):

    def test_first(self):
        correct = ['Initializing pubs in /paper_first.\n',
                   '',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n',
                   '',
                   '',
                   'search network\n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) search network\n'
                  ]

        cmds = ['pubs init -p paper_first/',
                'pubs add -d data/pagerank.pdf data/pagerank.bib',
                'pubs list',
                'pubs tag',
                'pubs tag Page99 network+search',
                'pubs tag Page99',
                'pubs tag search',
               ]

        self.assertEqual(correct, self.execute_cmds(cmds))

    def test_second(self):
        cmds = ['pubs init -p paper_second/',
                'pubs add data/pagerank.bib',
                'pubs add -d data/turing-mind-1950.pdf data/turing1950.bib',
                'pubs add data/martius.bib',
                'pubs add data/10.1371%2Fjournal.pone.0038236.bib',
                'pubs list',
                'pubs attach Page99 data/pagerank.pdf'
               ]
        self.execute_cmds(cmds)

    def test_third(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add -d data/turing-mind-1950.pdf data/turing1950.bib',
                'pubs add data/martius.bib',
                'pubs add data/10.1371%2Fjournal.pone.0038236.bib',
                'pubs list',
                'pubs attach Page99 data/pagerank.pdf',
                ('pubs remove Page99', ['y']),
                'pubs remove -f turing1950computing',
               ]
        self.execute_cmds(cmds)

    def test_editor_abort(self):
        with self.assertRaises(SystemExit):
            cmds = ['pubs init',
                    ('pubs add', ['abc', 'n']),
                    ('pubs add', ['abc', 'y', 'abc', 'n']),
                    'pubs add data/pagerank.bib',
                    ('pubs edit Page99', ['', 'a']),
                   ]
            self.execute_cmds(cmds)

    def test_editor_success(self):
        cmds = ['pubs init',
                ('pubs add', [str_fixtures.bibtex_external0]),
                ('pubs remove Page99', ['y']),
               ]
        self.execute_cmds(cmds)

    def test_edit(self):
        bib = str_fixtures.bibtex_external0
        bib1 = re.sub('year = \{1999\}', 'year = {2007}', bib)
        bib2 = re.sub('Lawrence Page', 'Lawrence Ridge', bib1)
        bib3 = re.sub('Page99', 'Ridge07', bib2)

        line = '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
        line1 = re.sub('1999', '2007', line)
        line2 = re.sub('Page,', 'Ridge,', line1)
        line3 = re.sub('Page99', 'Ridge07', line2)

        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ('pubs list', [], line),
                ('pubs edit Page99', [bib1]),
                ('pubs list', [], line1),
                ('pubs edit Page99', [bib2]),
                ('pubs list', [], line2),
                ('pubs edit Page99', [bib3]),
                ('pubs list', [], line3),
               ]
        self.execute_cmds(cmds)

    def test_export(self):
        cmds = ['pubs init',
                ('pubs add', [str_fixtures.bibtex_external0]),
                'pubs export Page99',
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(endecoder.EnDecoder().decode_bibdata(outs[2]), fixtures.page_bibdata)

    def test_import(self):
        cmds = ['pubs init',
                'pubs import data/',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(4 + 1, len(outs[-1].split('\n')))

    def test_import_one(self):
        cmds = ['pubs init',
                'pubs import data/ Page99',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_open(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs open Page99'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)

        with self.assertRaises(SystemExit):
            cmds[-1] == 'pubs open Page8'
            self.execute_cmds(cmds)

    def test_update(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs update'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)


if __name__ == '__main__':
    unittest.main()
