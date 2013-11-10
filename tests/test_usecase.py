import unittest
import re
import os

import testenv
import fake_env

from papers import papers_cmd
from papers import color, content, filebroker, uis, beets_ui, p3

import str_fixtures

from papers.commands import init_cmd, import_cmd

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

    def setUp(self):
        self.fs = fake_env.create_fake_fs([content, filebroker, init_cmd, import_cmd])

    def execute_cmds(self, cmds, fs=None):
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

                _, stdout, stderr = fake_env.redirect(papers_cmd.execute)(cmd[0].split())
                if len(cmd) == 3:
                    actual_out  = color.undye(stdout.getvalue())
                    correct_out = color.undye(cmd[2])
                    self.assertEqual(actual_out, correct_out)

            else:
                assert type(cmd) == str
                _, stdout, stderr = fake_env.redirect(papers_cmd.execute)(cmd.split())

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
        pubsdir = os.path.expanduser('~/papers_test2')
        papers_cmd.execute('papers init -p {}'.format(pubsdir).split())
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta'})

    def test_init2(self):
        pubsdir = os.path.expanduser('~/.papers')
        papers_cmd.execute('papers init'.split())
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta'})

class TestAdd(DataCommandTestCase):

    def test_add(self):
        cmds = ['papers init',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)

    def test_add2(self):
        cmds = ['papers init -p /not_default',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(self.fs['os'].listdir('/not_default/doc')), {'Page99.pdf'})


class TestList(DataCommandTestCase):

    def test_list(self):
        cmds = ['papers init -p /not_default2',
                'papers list',
                'papers add -b /data/pagerank.bib -d /data/pagerank.pdf',
                'papers list',
                ]
        self.execute_cmds(cmds)

    def test_list_smart_case(self):
        cmds = ['papers init',
                'papers list',
                'papers import data/',
                'papers list title:language author:Saunders',
                ]
        outs = self.execute_cmds(cmds)
        print outs[-1]
        self.assertEquals(1, len(outs[-1].split('/n')))

    def test_list_ignore_case(self):
        cmds = ['papers init',
                'papers list',
                'papers import data/',
                'papers list --ignore-case title:lAnguAge author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEquals(1, len(outs[-1].split('/n')))

    def test_list_force_case(self):
        cmds = ['papers init',
                'papers list',
                'papers import data/',
                'papers list --force-case title:Language author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEquals(0 + 1, len(outs[-1].split('/n')))



class TestUsecase(DataCommandTestCase):

    def test_first(self):
        correct = ['Initializing papers in /paper_first.\n',
                   '',
                   '[Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) \n',
                   '',
                   '',
                   'search network\n',
                   '[Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) search network\n'
                  ]

        cmds = ['papers init -p paper_first/',
                'papers add -d data/pagerank.pdf -b data/pagerank.bib',
                'papers list',
                'papers tag',
                'papers tag Page99 network+search',
                'papers tag Page99',
                'papers tag search',
               ]

        self.assertEqual(correct, self.execute_cmds(cmds))

    def test_second(self):
        cmds = ['papers init -p paper_second/',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf'
               ]
        self.execute_cmds(cmds)

    def test_third(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers add -d data/turing-mind-1950.pdf -b data/turing1950.bib',
                'papers add -b data/martius.bib',
                'papers add -b data/10.1371%2Fjournal.pone.0038236.bib',
                'papers list',
                'papers attach Page99 data/pagerank.pdf',
                ('papers remove Page99', ['y']),
                'papers remove -f turing1950computing',
               ]
        self.execute_cmds(cmds)

    def test_editor_abort(self):
        with self.assertRaises(SystemExit):
            cmds = ['papers init',
                    ('papers add', ['abc', 'n']),
                    ('papers add', ['abc', 'y', 'abc', 'n']),
                    'papers add -b data/pagerank.bib',
                    ('papers edit Page99', ['', 'a']),
                   ]
            self.execute_cmds(cmds)

    def test_editor_success(self):
        cmds = ['papers init',
                ('papers add', [str_fixtures.bibtex_external0]),
                ('papers remove Page99', ['y']),
               ]
        self.execute_cmds(cmds)

    def test_edit(self):
        bib = str_fixtures.bibtex_external0
        bib1 = re.sub('year = \{1999\}', 'year = {2007}', bib)
        bib2 = re.sub('Lawrence Page', 'Lawrence Ridge', bib1)
        bib3 = re.sub('Page99', 'Ridge07', bib2)

        line = '[Page99] L. Page et al. "The PageRank Citation Ranking Bringing Order to the Web"  (1999) \n'
        line1 = re.sub('1999', '2007', line)
        line2 = re.sub('L. Page', 'L. Ridge', line1)
        line3 = re.sub('Page99', 'Ridge07', line2)

        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                ('papers list', [], line),
                ('papers edit Page99', [bib1]),
                ('papers list', [], line1),
                ('papers edit Page99', [bib2]),
                ('papers list', [], line2),
                ('papers edit Page99', [bib3]),
                ('papers list', [], line3),
               ]

        self.execute_cmds(cmds)

    def test_export(self):
        cmds = ['papers init',
                ('papers add', [str_fixtures.bibtex_external0]),
                'papers export Page99',
                ('papers export Page99 -f bibtex', [], str_fixtures.bibtex_raw0),
                'papers export Page99 -f bibyaml',
               ]

        self.execute_cmds(cmds)

    def test_import(self):
        cmds = ['papers init',
                'papers import data/',
                'papers list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(4 + 1, len(outs[-1].split('\n')))

    def test_import_one(self):
        cmds = ['papers init',
                'papers import data/ Page99',
                'papers list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_open(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers open Page99'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)

        with self.assertRaises(SystemExit):
            cmds[-1] == 'papers open Page8'
            self.execute_cmds(cmds)

    def test_update(self):
        cmds = ['papers init',
                'papers add -b data/pagerank.bib',
                'papers update'
               ]

        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)
