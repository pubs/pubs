# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import unittest
import os
import re
import sys
import shutil

import six
import ddt
from pyfakefs.fake_filesystem import FakeFileOpen

import dotdot
import fake_env

from pubs import pubs_cmd, update, color, content, filebroker, uis, p3, endecoder
from pubs.config import conf
import configobj

import str_fixtures
import fixtures

from pubs.commands import init_cmd, import_cmd


# makes the tests very noisy
PRINT_OUTPUT   = False
CAPTURE_OUTPUT = True


class FakeSystemExit(Exception):
    """\
    SystemExit exceptions are replaced by FakeSystemExit in the execute_cmds()
    function, so they can be catched by ExpectedFailure tests in Python 2.x.

    If a code is expected to raise SystemExit, catch FakeSystemExit instead.

    Added explicit __init__ so SystemExit.code functionality could be emulated.
    Taking form from https://stackoverflow.com/a/26938914/1634191
    """
    def __init__(self, code=None, *args):
        self.code = code
        super(FakeSystemExit, self).__init__(
            "Exited with code: {}.".format(self.code), *args)


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
                                         module_list=[uis, color])
        other_input.as_global()
        self.assertEqual(uis._editor_input(), 'yes')
        self.assertEqual(uis._editor_input(), 'no')
        with self.assertRaises(fake_env.FakeInput.UnexpectedInput):
            color.input()


class CommandTestCase(fake_env.TestFakeFs):
    """Abstract TestCase intializing the fake filesystem."""

    maxDiff = 1000000

    def setUp(self, nsec_stat=True):
        super(CommandTestCase, self).setUp()
        os.stat_float_times(nsec_stat)
        # self.fs = fake_env.create_fake_fs([content, filebroker, conf, init_cmd, import_cmd, configobj, update], nsec_stat=nsec_stat)
        self.default_pubs_dir = os.path.expanduser('~/.pubs')
        self.default_conf_path = os.path.expanduser('~/.pubsrc')

    def execute_cmds(self, cmds, capture_output=CAPTURE_OUTPUT):
        """ Execute a list of commands, and capture their output

        A command can be a string, or a tuple of size 2, 3 or 4.
        In the latter case, the command is :
        1. a string reprensenting the command to execute
        2. the user inputs to feed to the command during execution
        3. the expected output on stdout, verified with assertEqual.
        4. the expected output on stderr, verified with assertEqual.
        """
        try:
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
                        capture_wrap = fake_env.capture(pubs_cmd.execute,
                                                        verbose=PRINT_OUTPUT)
                        _, stdout, stderr = capture_wrap(actual_cmd.split())
                        actual_out = color.undye(stdout)
                        actual_err = color.undye(stderr)
                        if expected_out is not None:
                            self.assertEqual(p3.u_maybe(actual_out), p3.u_maybe(expected_out))
                        if expected_err is not None:
                            self.assertEqual(p3.u_maybe(actual_err), p3.u_maybe(expected_err))
                        outs.append(color.undye(actual_out))
                    else:
                        pubs_cmd.execute(actual_cmd.split())
                except fake_env.FakeInput.UnexpectedInput as e:
                    self.fail('Unexpected input asked by command: {}.'.format(
                        actual_cmd))
            return outs
        except SystemExit as exc:
            exc_class, exc, tb = sys.exc_info()
            if sys.version_info.major == 2:
                # using six to avoid a SyntaxError in Python 3.x
                six.reraise(FakeSystemExit, FakeSystemExit(*exc.args), tb)
            else:
                raise FakeSystemExit(*exc.args).with_traceback(tb)

    def tearDown(self):
        pass


class DataCommandTestCase(CommandTestCase):
    """Abstract TestCase intializing the fake filesystem and
    copying fake data.
    """

    def setUp(self, nsec_stat=True):
        super(DataCommandTestCase, self).setUp(nsec_stat=nsec_stat)
        self.fs.add_real_directory(os.path.join(self.rootpath, 'data'), read_only=False)
        self.fs.add_real_directory(os.path.join(self.rootpath, 'bibexamples'), read_only=False)

        # fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'data'), 'data')
        # fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'bibexamples'), 'bibexamples')

    def assertFileContentEqual(self, path, expected_content):
        self.assertTrue(os.path.isfile(path))
        self.assertEqual(content.get_content(path), expected_content)


class URLContentTestCase(DataCommandTestCase):
    """Mocks access to online files by using files in data directory.
    """

    def setUp(self):
        super(URLContentTestCase, self).setUp()
        self._original_get_byte_url_content = content._get_byte_url_content
        self._original_url_exist = content.url_exists
        content._get_byte_url_content = self.url_to_byte_content
        content.url_exists = self.url_exists

    def _url_to_path(self, url):
        return p3.urlparse(url).path

    def url_exists(self, url):
        return self.fs.Exists(self._url_to_path(url))

    def url_to_byte_content(self, url, ui=None):
        path = self._url_to_path(url)
        with FakeFileOpen(self.fs)('data' + path, 'rb') as f:
            return f.read()

    def tearDown(self):
        super(URLContentTestCase, self).tearDown()
        content._get_byte_url_content = self._original_get_byte_url_content
        content.url_exists = self._original_url_exist


# Actual tests

class TestAlone(CommandTestCase):

    def test_alone_misses_command(self):
        with self.assertRaises(FakeSystemExit) as cm:
            self.execute_cmds(['pubs'])
            self.assertEqual(cm.exception.code, 2)

    def test_alone_prints_help(self):
        # capturing the output of `pubs --help` is difficult because argparse
        # raises as SystemExit(0) after calling `print_help`, and this gets
        # caught so no output is captured.  so comparing outputs of `pubs` and
        # `pubs --help` isn't too easy unless substantially reorganization of
        # the parser and testing context is made.  instead, the exit codes of
        # the two usecases are compared.
        with self.assertRaises(FakeSystemExit) as cm1:
            self.execute_cmds(['pubs'])
        self.assertEqual(cm1.exception.code, 2)

    def test_help_prints_help(self):
        # see test_alone_prints_help
        with self.assertRaises(FakeSystemExit) as cm2:
            self.execute_cmds(['pubs init', 'pubs --help'])
        self.assertEqual(cm2.exception.code, 0)


class TestInit(CommandTestCase):

    def test_init(self):
        pubsdir = os.path.expanduser('~/pubs_test2')
        self.execute_cmds(['pubs init -p {}'.format(pubsdir)])
        self.assertEqual(set(os.listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes', '.cache'})

    def test_init2(self):
        pubsdir = os.path.expanduser('~/.pubs')
        self.execute_cmds(['pubs init'])
        self.assertEqual(set(os.listdir(pubsdir)),
                         {'bib', 'doc', 'meta', 'notes', '.cache'})

    def test_init_config(self):
        self.execute_cmds(['pubs init'])
        self.assertTrue(os.path.isfile(self.default_conf_path))


class TestAdd(URLContentTestCase):

    def test_add(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        bib_dir = os.path.join(self.default_pubs_dir, 'bib')
        meta_dir = os.path.join(self.default_pubs_dir, 'meta')
        doc_dir = os.path.join(self.default_pubs_dir, 'doc')
        self.assertEqual(set(os.listdir(bib_dir)), {'Page99.bib'})
        self.assertEqual(set(os.listdir(meta_dir)), {'Page99.yaml'})
        self.assertEqual(set(os.listdir(doc_dir)), {'Page99.pdf'})

    def test_add_bibutils(self):
        cmds = ['pubs init',
                'pubs add bibexamples/bibutils.bib',
                ]
        self.execute_cmds(cmds)
        bib_dir = os.path.join(self.default_pubs_dir, 'bib')
        self.assertEqual(set(os.listdir(bib_dir)), {'Page99.bib'})

    def test_add_other_repository_path(self):
        cmds = ['pubs init -p /not_default',
                'pubs add data/pagerank.bib -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(os.listdir('/not_default/doc')), {'Page99.pdf'})

    def test_add_citekey(self):
        cmds = ['pubs init',
                'pubs add -k CustomCitekey data/pagerank.bib',
                ]
        self.execute_cmds(cmds)
        bib_dir = os.path.join(self.default_pubs_dir, 'bib')
        self.assertEqual(set(os.listdir(bib_dir)), {'CustomCitekey.bib'})

    def test_add_utf8_citekey(self):
        correct = ["",
                   ("added to pubs:\n"
                    "[hausdorff1949grundzüge] Hausdorff, Felix \"Grundzüge der Mengenlehre\" (1949) \n"),
                   "The 'hausdorff1949grundzüge' citekey has been renamed into 'アスキー'\n",
                   "The 'アスキー' citekey has been renamed into 'Ḽơᶉëᶆ_ȋṕšᶙṁ'\n"
                  ]
        cmds = ['pubs init',
                ('pubs add bibexamples/utf8.bib', [], correct[1]),
                ('pubs rename hausdorff1949grundzüge アスキー', [], correct[2]),
                ('pubs rename アスキー Ḽơᶉëᶆ_ȋṕšᶙṁ', [], correct[3]),
               ]
        self.execute_cmds(cmds)

    def test_add_doc_nocopy_does_not_copy(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --link -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(os.listdir(
                os.path.join(self.default_pubs_dir, 'doc')),
            [])

    def test_add_move_removes_doc(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --move -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertFalse(os.path.exists('data/pagerank.pdf'))

    def test_add_twice_fails(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add -k Page99 data/turing1950.bib',
                ]
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

    def test_add_urls(self):
        cmds = ['pubs init',
                'pubs add http://host.xxx/pagerank.bib '
                '-d http://host.xxx/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        bib_dir = os.path.join(self.default_pubs_dir, 'bib')
        self.assertEqual(set(os.listdir(bib_dir)), {'Page99.bib'})
        meta_dir = os.path.join(self.default_pubs_dir, 'meta')
        self.assertEqual(set(os.listdir(meta_dir)), {'Page99.yaml'})
        doc_dir = os.path.join(self.default_pubs_dir, 'doc')
        self.assertEqual(set(os.listdir(doc_dir)), {'Page99.pdf'})

    def test_leading_citekey_space(self):
        cmds = ['pubs init',
                'pubs add bibexamples/leadingspace.bib',
                'pubs rename LeadingSpace NoLeadingSpace',
               ]
        self.execute_cmds(cmds)

    def test_add_no_citekey_fails(self):
        # See #113
        cmds = ['pubs init',
                ('pubs add', [str_fixtures.bibtex_no_citekey]),
                ]
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)


class TestList(DataCommandTestCase):

    def test_list(self):
        cmds = ['pubs init -p /not_default2',
                'pubs list',
                'pubs add data/pagerank.bib -d data/pagerank.pdf',
                'pubs list',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(0, len(outs[1].splitlines()))
        self.assertEqual(1, len(outs[3].splitlines()))

    def test_list_several_no_date(self):
        self.execute_cmds(['pubs init -p testrepo'])
        os.chdir('/') # weird fix for shutil.rmtree invocation.
        shutil.rmtree(self.rootpath + '/testrepo')
        os.chdir(self.rootpath)
        self.fs.add_real_directory(os.path.join(self.rootpath, 'testrepo'), read_only=False)

        #fake_env.copy_dir(self.fs, testrepo, 'testrepo')
        cmds = ['pubs list',
                'pubs remove -f Page99',
                'pubs list',
                'pubs add data/pagerank.bib -d data/pagerank.pdf',
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

    def test_list_strict_forces_case(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --ignore-case --strict title:lAnguage',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(0 + 1, len(outs[-1].split('\n')))

    def test_list_strict(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list --strict title:{L}anguage',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(0 + 1, len(outs[-1].split('\n')))

    def test_list_latex_protection(self):
        cmds = ['pubs init',
                'pubs list',
                'pubs import data/',
                'pubs list title:{L}anguage',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))


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
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)


class TestNote(DataCommandTestCase):

    def setUp(self):
        super(TestNote, self).setUp()
        init = ['pubs init',
                'pubs add data/pagerank.bib',
                ]
        self.execute_cmds(init)
        self.note_dir = os.path.join(self.default_pubs_dir, 'notes')

    def test_note_edit(self):
        cmds = [('pubs note Page99', ['xxx']),
                ]
        self.execute_cmds(cmds)
        self.assertFileContentEqual(os.path.join(self.note_dir, 'Page99.txt'),
                                    'xxx')

    def test_note_edit_extension(self):
        config = conf.load_conf()
        config['main']['note_extension'] = 'md'
        conf.save_conf(config)
        cmds = [('pubs note Page99', ['xxx']),
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(os.listdir(self.note_dir)), {'Page99.md'})
        self.assertFileContentEqual(os.path.join(self.note_dir, 'Page99.md'),
                                    'xxx')

    def test_rename_with_note(self):
        config = conf.load_conf()
        conf.save_conf(config)
        cmds = [('pubs note Page99', ['xxx']),
                'pubs rename Page99 Page1999',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(os.listdir(self.note_dir)), {'Page1999.txt'})
        self.assertFileContentEqual(os.path.join(self.note_dir, 'Page1999.txt'),
                                    'xxx')

    def test_rename_with_note_extension(self):
        config = conf.load_conf()
        config['main']['note_extension'] = 'md'
        conf.save_conf(config)
        cmds = [('pubs note Page99', ['xxx']),
                'pubs rename Page99 Page1999',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(set(os.listdir(self.note_dir)), {'Page1999.md'})
        self.assertFileContentEqual(os.path.join(self.note_dir, 'Page1999.md'),
                                    'xxx')

    def test_remove_with_note_extension(self):
        config = conf.load_conf()
        config['main']['note_extension'] = 'md'
        conf.save_conf(config)
        cmds = [('pubs note Page99', ['xxx']),
                ('pubs remove Page99', ['y']),
                ]
        self.execute_cmds(cmds)
        self.assertEqual(os.listdir(self.note_dir), [])


class TestUsecase(DataCommandTestCase):

    def test_first(self):
        correct = ['Initializing pubs in /paper_first\n',
                   'added to pubs:\n[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
                   'data/pagerank.pdf was copied to the pubs repository.\n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n',
                   '\n',
                   '',
                   'network search\n',
                   'info: Assuming search to be a tag.\n'
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | network,search\n',
                  ]

        cmds = ['pubs init -p /paper_first',
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
                'pubs doc add data/pagerank.pdf Page99'
               ]
        self.execute_cmds(cmds)

    def test_third(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add -d data/turing-mind-1950.pdf data/turing1950.bib',
                'pubs add data/martius.bib',
                'pubs add data/10.1371%2Fjournal.pone.0038236.bib',
                'pubs list',
                'pubs doc add data/pagerank.pdf Page99',
                ('pubs remove Page99', ['y']),
                'pubs remove -f turing1950computing',
               ]
        self.execute_cmds(cmds)
        docdir = os.path.expanduser('~/.pubs/doc/')
        self.assertNotIn('turing-mind-1950.pdf', os.listdir(docdir))

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

    def test_conf(self):
        cmds = ['pubs init',
                ('pubs conf', [str_fixtures.sample_conf]),
               ]
        self.execute_cmds(cmds)
        self.assertFileContentEqual(os.path.expanduser('~/.pubsrc'),
                                    str_fixtures.sample_conf)

    def test_editor_abort(self):
        with self.assertRaises(FakeSystemExit):
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

    def test_edit_meta(self):
        meta = str_fixtures.turing_meta

        line = '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
        line1 = re.sub('\n', '| AI,computer\n', line)

        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ('pubs list', [], line),
                ('pubs edit -m Page99', [meta]),
                ('pubs list', [], line1),
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

    def test_export_ignore_field(self):
        cmds = ['pubs init',
                ('pubs add', [str_fixtures.bibtex_external0]),
                'pubs export --ignore-fields author,title Page99',
                ]
        outs = self.execute_cmds(cmds)
        expected = endecoder.EnDecoder().encode_bibdata(
            fixtures.page_bibentry, ignore_fields=['author', 'title'])
        self.assertEqual(outs[2], expected + os.linesep)

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

    def test_import_does_not_overwrite(self):
        cmds = ['pubs init',
                'pubs import data/ Page99',
                'pubs import data/',
                'pubs list'
               ]

        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

    def test_import_overwrites(self):
        cmds = ['pubs init',
                'pubs import data/ Page99',
                'pubs import --overwrite data/ Page99',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_update(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs update'
               ]

        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

    def test_add_with_tag(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --tags junk',
                'pubs tag junk'
               ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(2, len(outs[2].splitlines()))

    def test_doc_open(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs doc open Page99'
               ]
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)
        with self.assertRaises(FakeSystemExit):
            cmds[-1] == 'pubs doc open Page8'
            self.execute_cmds(cmds)

    def test_doc_add(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs doc add data/pagerank.pdf Page99'
               ]
        self.execute_cmds(cmds)
        self.assertTrue(os.path.exists(
            os.path.join(self.default_pubs_dir,
                                    'doc',
                                    'Page99.pdf')))
        # Also test that do not remove original
        self.assertTrue(os.path.exists('data/pagerank.pdf'))

    def test_doc_add_with_move(self):
        cmds = ['pubs init -p paper_second/',
                'pubs add data/pagerank.bib',
                'pubs doc add --move data/pagerank.pdf Page99'
               ]
        self.execute_cmds(cmds)
        self.assertFalse(os.path.exists('data/pagerank.pdf'))

    def test_doc_remove(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs doc add data/pagerank.pdf Page99',
                ('pubs doc remove Page99', ['y']),
               ]
        self.execute_cmds(cmds)
        docdir = os.path.expanduser('~/.pubs/doc/')
        self.assertNotIn('turing-mind-1950.pdf', os.listdir(docdir))

    def test_doc_export(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs rename Page99 page100',
                'pubs doc add data/pagerank.pdf page100',
                'pubs doc export page100 /'
                ]
        self.execute_cmds(cmds)
        self.assertIn('page100.pdf', os.listdir('/'))


    def test_alternate_config(self):
        alt_conf = os.path.expanduser('~/.alt_conf')
        cmds = ['pubs -c ' + alt_conf + ' init',
                'pubs --config ' + alt_conf + ' import data/ Page99',
                'pubs list -c ' + alt_conf
               ]
        outs = self.execute_cmds(cmds)
        # check if pubs works as expected
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))
        # check whether we actually changed the config file
        self.assertFalse(os.path.isfile(self.default_conf_path))
        self.assertTrue(os.path.isfile(alt_conf))



@ddt.ddt
class TestCache(DataCommandTestCase):
    """\
    Run tests on fake filesystems supporting both integers and nanosecond
    stat times.
    """

    def setUp(self):
        pass

    @ddt.data(True, False)
    def test_remove(self, nsec_stat):
        DataCommandTestCase.setUp(self, nsec_stat=nsec_stat)
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ('pubs remove Page99', ['y']),
                'pubs list',
               ]
        out = self.execute_cmds(cmds)
        self.assertEqual(1, len(out[3].split('\n')))

    @ddt.data(True, False)
    def test_edit(self, nsec_stat):
        DataCommandTestCase.setUp(self, nsec_stat=nsec_stat)

        bib = str_fixtures.bibtex_external0
        bib1 = re.sub('year = \{1999\}', 'year = {2007}', bib)

        line = '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
        line1 = re.sub('1999', '2007', line)

        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs list',
                ('pubs edit Page99', [bib1]),
                'pubs list',
               ]

        out = self.execute_cmds(cmds)
        self.assertEqual(line,  out[2])
        self.assertEqual(line1, out[4])


if __name__ == '__main__':
    unittest.main()
