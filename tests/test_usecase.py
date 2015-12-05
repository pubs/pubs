from __future__ import print_function, unicode_literals

import unittest
import re
import os

import dotdot
import fake_env

from pubs import pubs_cmd
from pubs import color, content, filebroker, uis, p3, endecoder, configs

import str_fixtures
import fixtures

from pubs.commands import init_cmd, import_cmd


# makes the tests very noisy
messagePUT=False
CAPTURE_OUTPUT=True


# code for fake fs

class TestFakeInput(unittest.TestCase):

    def test_input(self):
        input = fake_env.FakeInput(['yes', 'no'])
        self.assertEqual(input(), 'yes')
        self.assertEqual(input(), 'no')
        with self.assertRaises(fake_env.FakeInput.UnexpectedInput):
            input()

    def test_input2(self):
        other_input = fake_env.FakeInput(['yes', 'no'], module_list=[color])
        other_input.as_global()
        self.assertEqual(color.input(), 'yes')
        self.assertEqual(color.input(), 'no')
        with self.assertRaises(fake_env.FakeInput.UnexpectedInput):
            color.input()

    def test_editor_input(self):
        other_input = fake_env.FakeInput(['yes', 'no'],
                                         module_list=[content, color])
        other_input.as_global()
        self.assertEqual(content.editor_input(), 'yes')
        self.assertEqual(content.editor_input(), 'no')
        with self.assertRaises(fake_env.FakeInput.UnexpectedInput):
            color.input()


class CommandTestCase(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    maxDiff = 1000000

    def setUp(self):
        self.fs = fake_env.create_fake_fs([content, filebroker, configs, init_cmd, import_cmd])
        self.default_pubs_dir = self.fs['os'].path.expanduser('~/.pubs')

    def execute_cmds(self, cmds, capture_output=CAPTURE_OUTPUT):
        """ Execute a list of commands, and capture their output

        A command can be a string, or a tuple of size 2, 3 or 4.
        In the latter case, the command is :
        1. a string reprensenting the command to execute
        2. the user inputs to feed to the command during execution
        3. the expected output on stdout, verified with assertEqual.
        4. the expected output on stderr, verified with assertEqual.
        """
        outs = []
        for cmd in cmds:
            inputs = []
            expected_out, expected_err = None, None
            actual_cmd = cmd
            if not isinstance(cmd, p3.ustr):
                actual_cmd = cmd[0]
                if len(cmd) == 2:  # Inputs provided
                    inputs = cmd[1]
                if len(cmd) == 3:  # Expected output provided
                    capture_output = True
                    expected_out = color.undye(cmd[2])
                if len(cmd) == 4:  # Expected error output provided
                    expected_err = color.undye(cmd[3])
            # Always set fake input: test should not ask unexpected user input
            input = fake_env.FakeInput(inputs, [content, uis, p3])
            input.as_global()
            try:
                if capture_output:
                    _, stdout, stderr = fake_env.redirect(pubs_cmd.execute)(
                        actual_cmd.split())
                    actual_out = color.undye(stdout)
                    actual_err = color.undye(stderr)
                    if expected_out is not None:
                        self.assertEqual(actual_out, expected_out)
                    if expected_err is not None:
                        self.assertEqual(actual_err, expected_err)
                    outs.append(color.undye(actual_out))
                else:
                    pubs_cmd.execute(actual_cmd.split())
            except fake_env.FakeInput.UnexpectedInput:
                self.fail('Unexpected input asked by command: {}.'.format(
                    actual_cmd))
        if messagePUT:
            print(outs)
        return outs

    def tearDown(self):
        fake_env.unset_fake_fs([content, filebroker, configs, init_cmd, import_cmd])


class DataCommandTestCase(CommandTestCase):
    """Abstract TestCase intializing the fake filesystem and
    copying fake data.
    """

    def setUp(self):
        super(DataCommandTestCase, self).setUp()
        fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'data'), 'data')


# Actual tests

class TestInit(CommandTestCase):

    def test_init(self):
        pubsdir = os.path.expanduser('~/pubs_test2')
        self.execute_cmds(['pubs init -p {}'.format(pubsdir)])
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes'})

    def test_init2(self):
        pubsdir = os.path.expanduser('~/.pubs')
        self.execute_cmds(['pubs init'])
        self.assertEqual(set(self.fs['os'].listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes'})


class TestAdd(DataCommandTestCase):

    def test_add(self):
        cmds = ['pubs init',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        bib_dir = self.fs['os'].path.join(self.default_pubs_dir, 'bib')
        meta_dir = self.fs['os'].path.join(self.default_pubs_dir, 'meta')
        doc_dir = self.fs['os'].path.join(self.default_pubs_dir, 'doc')
        self.assertEqual(set(self.fs['os'].listdir(bib_dir)), {'Page99.bib'})
        self.assertEqual(set(self.fs['os'].listdir(meta_dir)), {'Page99.yaml'})
        self.assertEqual(set(self.fs['os'].listdir(doc_dir)), {'Page99.pdf'})

    def test_add2(self):
        cmds = ['pubs init -p /not_default',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(self.fs['os'].listdir('/not_default/doc')), {'Page99.pdf'})

    def test_add_citekey(self):
        cmds = ['pubs init',
                'pubs add -k CustomCitekey /data/pagerank.bib',
                ]
        self.execute_cmds(cmds)
        bib_dir = self.fs['os'].path.join(self.default_pubs_dir, 'bib')
        self.assertEqual(set(self.fs['os'].listdir(bib_dir)), {'CustomCitekey.bib'})

    def test_add_doc_nocopy_does_not_copy(self):
        cmds = ['pubs init',
                'pubs add /data/pagerank.bib --link -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(self.fs['os'].listdir(
                self.fs['os'].path.join(self.default_pubs_dir, 'doc')),
            [])

    def test_add_move_removes_doc(self):
        cmds = ['pubs init',
                'pubs add /data/pagerank.bib --move -d /data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertFalse(self.fs['os'].path.exists('/data/pagerank.pdf'))

    def test_add_twice_fails(self):
        cmds = ['pubs init',
                'pubs add /data/pagerank.bib',
                'pubs add -k Page99 /data/turing1950.bib',
                ]
        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)


class TestList(DataCommandTestCase):

    def test_list(self):
        cmds = ['pubs init -p /not_default2',
                'pubs list',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                'pubs list',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(0, len(outs[1].splitlines()))
        self.assertEqual(1, len(outs[3].splitlines()))

    def test_list_several_no_date(self):
        self.execute_cmds(['pubs init -p /testrepo'])
        self.fs['shutil'].rmtree('testrepo')
        testrepo = os.path.join(os.path.dirname(__file__), 'testrepo')
        fake_env.copy_dir(self.fs, testrepo, 'testrepo')
        cmds = ['pubs list',
                'pubs remove -f Page99',
                'pubs list',
                'pubs add /data/pagerank.bib -d /data/pagerank.pdf',
                'pubs list',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(4, len(outs[0].splitlines()))
        self.assertEqual(3, len(outs[2].splitlines()))
        self.assertEqual(4, len(outs[4].splitlines()))
        # Last added should be last
        self.assertEqual('[Page99]', outs[4].splitlines()[-1][:8])

    def test_list_smart_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list title:language author:Saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1, len(outs[-1].splitlines()))

    def test_list_ignore_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --ignore-case title:lAnguAge author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1, len(outs[-1].splitlines()))

    def test_list_force_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --force-case title:Language author:saunders',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(0 + 1, len(outs[-1].split('\n')))


class TestTag(DataCommandTestCase):

    def setUp(self):
        super(TestTag, self).setUp()
        init = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add -k Turing1950 data/turing1950.bib',
               ]
        self.execute_cmds(init)

    def test_add_tag(self):
        cmds = ['pubs tag Page99 search',
                'pubs tag Turing1950 ai',
                'pubs list',
                ]
        correct = ['',
                   '',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | search\n' +
                   '[Turing1950] Turing, Alan M "Computing machinery and intelligence" Mind (1950) | ai\n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)

    def test_add_tags(self):
        """Adds several tags at once.
        Also checks that tags printed in alphabetic order.
        """
        cmds = ['pubs tag Page99 search+network',
                'pubs list',
                ]
        correct = ['',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | network,search\n' +
                   '[Turing1950] Turing, Alan M "Computing machinery and intelligence" Mind (1950) \n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)

    def test_remove_tag(self):
        cmds = ['pubs tag Page99 search+network',
                'pubs tag Page99 :network',
                'pubs list',
                ]
        correct = ['',
                   '',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | search\n' +
                   '[Turing1950] Turing, Alan M "Computing machinery and intelligence" Mind (1950) \n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)

    def test_add_remove_tag(self):
        cmds = ['pubs tag Page99 a',
                'pubs tag Page99 b-a',
                'pubs list',
                ]
        correct = ['',
                   '',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | b\n' +
                   '[Turing1950] Turing, Alan M "Computing machinery and intelligence" Mind (1950) \n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)

    def test_wrong_citekey(self):
        cmds = ['pubs tag Page999 a',
                ]
        with self.assertRaises(SystemExit):
            self.execute_cmds(cmds)


class TestUsecase(DataCommandTestCase):

    def test_first(self):
        correct = ['Initializing pubs in /paper_first\n',
                   'added to pubs:\n[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n',
                   '\n',
                   '',
                   'network search\n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | network,search\n',
                  ]

        cmds = ['pubs init -p paper_first/',
                'pubs add -d data/pagerank.pdf data/pagerank.bib',
                'pubs list',
                'pubs tag',
                'pubs tag Page99 network+search',
                'pubs tag Page99',
                'pubs tag search',
               ]

        self.assertEqual(correct, self.execute_cmds(cmds, capture_output=True))

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
        docdir = self.fs['os'].path.expanduser('~/.pubs/doc/')
        self.assertNotIn('turing-mind-1950.pdf', self.fs['os'].listdir(docdir))

    def test_tag_list(self):
        correct = ['Initializing pubs in /paper_first\n',
                   '',
                   '',
                   '',
                   'search network\n',
                  ]

        cmds = ['pubs init -p paper_first/',
                'pubs add -d data/pagerank.pdf data/pagerank.bib',
                'pubs tag',
                'pubs tag Page99 network+search',
                'pubs tag',
               ]

        out = self.execute_cmds(cmds)

        def clean(s):
            return set(s.strip().split(' '))

        self.assertEqual(clean(correct[2]), clean(out[2]))
        self.assertEqual(clean(correct[4]), clean(out[4]))

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
        self.assertEqual(endecoder.EnDecoder().decode_bibdata(outs[2]),
                         fixtures.page_bibentry)

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

    def test_add_with_tag(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --tags junk',
                'pubs tag junk'
               ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1, len(outs[2].splitlines()))

    def test_attach(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs attach Page99 data/pagerank.pdf'
               ]
        self.execute_cmds(cmds)
        self.assertTrue(self.fs['os'].path.exists(
            self.fs['os'].path.join(self.default_pubs_dir,
                                    'doc',
                                    'Page99.pdf')))
        # Also test that do not remove original
        self.assertTrue(self.fs['os'].path.exists('/data/pagerank.pdf'))

    def test_attach_with_move(self):
        cmds = ['pubs init -p paper_second/',
                'pubs add data/pagerank.bib',
                'pubs attach --move Page99 data/pagerank.pdf'
               ]
        self.execute_cmds(cmds)
        self.assertFalse(self.fs['os'].path.exists('/data/pagerank.pdf'))
    

if __name__ == '__main__':
    unittest.main()
