# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import unittest
import os
import re
import sys
import shutil

import six
import ddt
import certifi
import mock
from pyfakefs.fake_filesystem import FakeFileOpen
import pytest

import dotdot
import fake_env
import mock_requests


from pubs import pubs_cmd, color, content, uis, p3, endecoder
from pubs.config import conf

import str_fixtures
import fixtures


# makes the tests very noisy
PRINT_OUTPUT   = True #False
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


class TestInput(unittest.TestCase):
    """Test that the fake input mechanisms work correctly in the tests"""

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
        sample_conf = conf.load_default_conf()
        ui = uis.InputUI(sample_conf)

        other_input = fake_env.FakeInput(['yes', 'no'],
                                         module_list=[uis])
        other_input.as_global()
        self.assertEqual(ui.editor_input('fake_editor'), 'yes')
        self.assertEqual(ui.editor_input('fake_editor'), 'no')
        with self.assertRaises(fake_env.FakeInput.UnexpectedInput):
            ui.editor_input()


class CommandTestCase(fake_env.TestFakeFs):
    """Abstract TestCase intializing the fake filesystem."""

    maxDiff = 1000000

    def setUp(self):
        super(CommandTestCase, self).setUp()
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
                    if len(cmd) >= 2 and cmd[1] is not None:  # Inputs provided
                        inputs = cmd[1]
                    if len(cmd) >= 3:  # Expected output provided
                        capture_output = True
                        if cmd[2] is not None:
                            expected_out = color.undye(cmd[2])
                    if len(cmd) >= 4 and cmd[3] is not None:  # Expected error output provided
                            expected_err = color.undye(cmd[3])
                # Always set fake input: test should not ask unexpected user input
                input = fake_env.FakeInput(inputs, [content, uis, p3])
                input.as_global()
                try:
                    if capture_output:
                        actual_out = self.execute_cmd_capture(actual_cmd.split(), expected_out, expected_err)
                        outs.append(color.undye(actual_out))
                    else:
                        pubs_cmd.execute(actual_cmd.split())
                except fake_env.FakeInput.UnexpectedInput:
                    self.fail('Unexpected input asked by command: {}.'.format(actual_cmd))
            return outs
        except SystemExit as exc:
            exc_class, exc, tb = sys.exc_info()
            if sys.version_info.major == 2:
                # using six to avoid a SyntaxError in Python 3.x
                six.reraise(FakeSystemExit, FakeSystemExit(*exc.args), tb)
            else:
                raise FakeSystemExit(*exc.args).with_traceback(tb)

    @staticmethod
    def normalize(s):
        """Remove color from a string, adjusting for a decode method needed in Python2"""
        s = color.undye(s)
        try:
            s = s.decode('utf-8')
        except AttributeError:
            pass
        return s

    def execute_cmd_capture(self, cmd, expected_out, expected_err):
        """Run a single command, captures the output and and stderr and compare it to the expected ones"""
        sys_stdout, sys_stderr = sys.stdout, sys.stderr
        sys.stdout = p3._fake_stdio(additional_out=sys_stdout if PRINT_OUTPUT else None)
        sys.stderr = p3._fake_stdio(additional_out=sys_stderr if PRINT_OUTPUT else None)

        try:
            pubs_cmd.execute(cmd)
        finally:
            # capturing output even if exception was raised.
            self.captured_stdout = self.normalize(p3._get_fake_stdio_ucontent(sys.stdout))
            self.captured_stderr = self.normalize(p3._get_fake_stdio_ucontent(sys.stderr))
            sys.stderr, sys.stdout = sys_stderr, sys_stdout

        if expected_out is not None:
            self.assertEqual(p3.u_maybe(self.captured_stdout), p3.u_maybe(expected_out))
        if expected_err is not None:
            self.assertEqual(p3.u_maybe(self.captured_stderr), p3.u_maybe(expected_err))
        return self.captured_stdout

    def update_config(self, config_update, path=None):
        """Allow to set the config parameters. Must have done a `pubs init` beforehand."""
        if path is None:
            path = self.default_conf_path
        cfg = conf.load_conf(path=path)
        for section, section_update in config_update.items():
            cfg[section].update(section_update)
        conf.save_conf(cfg, path=path)



class DataCommandTestCase(CommandTestCase):
    """Abstract TestCase intializing the fake filesystem and copying fake data."""

    def setUp(self):
        super(DataCommandTestCase, self).setUp()
        self.fs.add_real_directory(os.path.join(self.rootpath, 'data'), read_only=False)
        self.fs.add_real_directory(os.path.join(self.rootpath, 'bibexamples'), read_only=False)
        # add certificate for web querries
        self.fs.add_real_file(certifi.where(), read_only=True)
        self.fs.add_real_file(mock_requests._data_filepath, read_only=False)


    def assertFileContentEqual(self, path, expected_content):
        self.assertTrue(os.path.isfile(path))
        self.assertEqual(content.get_content(path), expected_content)


class URLContentTestCase(DataCommandTestCase):
    """Mocks access to online files by using files in data directory."""

    def setUp(self):
        super(URLContentTestCase, self).setUp()
        self._original_get_byte_url_content = content._get_byte_url_content
        self._original_url_exist = content.url_exists
        content._get_byte_url_content = self.url_to_byte_content
        content.url_exists = self.url_exists

    def _url_to_path(self, url):
        return p3.urlparse(url).path

    def url_exists(self, url):
        return self.fs.exists(self._url_to_path(url))

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
                    "[hausdorff1949grundzüge] Hausdorff, Felix \"Grundzüge der Mengenlehre\" (1949) \n"),
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
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            [])
        self.assertTrue(os.path.exists('data/pagerank.pdf'))

    def test_add_doc_nocopy_from_config_does_not_copy(self):
        self.execute_cmds(['pubs init'])
        config = conf.load_conf()
        config['main']['doc_add'] = 'link'
        conf.save_conf(config)
        cmds = ['pubs add data/pagerank.bib -d data/pagerank.pdf']
        self.execute_cmds(cmds)
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            [])
        self.assertTrue(os.path.exists('data/pagerank.pdf'))

    def test_add_doc_copy(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --copy -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            ['Page99.pdf'])
        self.assertTrue(os.path.exists('data/pagerank.pdf'))

    def test_add_doc_copy_from_config(self):
        self.execute_cmds(['pubs init'])
        config = conf.load_conf()
        config['main']['doc_add'] = 'copy'
        conf.save_conf(config)
        cmds = ['pubs add data/pagerank.bib -d data/pagerank.pdf']
        self.execute_cmds(cmds)
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            ['Page99.pdf'])
        self.assertTrue(os.path.exists('data/pagerank.pdf'))

    def test_add_doc_move(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib --move -d data/pagerank.pdf',
                ]
        self.execute_cmds(cmds)
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            ['Page99.pdf'])
        self.assertFalse(os.path.exists('data/pagerank.pdf'))

    def test_add_doc_move_from_config(self):
        self.execute_cmds(['pubs init'])
        config = conf.load_conf()
        config['main']['doc_add'] = 'move'
        conf.save_conf(config)
        cmds = ['pubs add data/pagerank.bib -d data/pagerank.pdf']
        self.execute_cmds(cmds)
        self.assertEqual(
            os.listdir(os.path.join(self.default_pubs_dir, 'doc')),
            ['Page99.pdf'])
        self.assertFalse(os.path.exists('data/pagerank.pdf'))

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
                ('pubs add', [str_fixtures.bibtex_no_citekey, 'n']),
                ]
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

    def test_add_edit_fails(self):
        cmds = ['pubs init',
                ('pubs add',
                    ['@misc{I am not a correct bibtex{{}', 'n']),
                ]
        with self.assertRaises(FakeSystemExit) as cm:
            self.execute_cmds(cmds)
        self.assertEqual(cm.exception.code, 1)

    def test_add_excludes_bibtex_fields(self):
        self.execute_cmds(['pubs init'])
        config = conf.load_conf()
        config['main']['exclude_bibtex_fields'] = ['abstract', 'publisher']
        conf.save_conf(config)
        self.execute_cmds(['pubs add data/pagerank.bib'])
        with FakeFileOpen(self.fs)(self.default_pubs_dir + '/bib/Page99.bib', 'r') as buf:
            out = endecoder.EnDecoder().decode_bibdata(buf.read())
        for bib in out.values():
            self.assertFalse('abstract' in bib or 'publisher' in bib)
            self.assertTrue('title' in bib and 'author' in bib)


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
        os.chdir('/')  # weird fix for shutil.rmtree invocation.
        shutil.rmtree(os.path.join(self.rootpath, 'testrepo'))
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

    def test_list_with_citekey_query(self):
        cmds = ['pubs init',
                'pubs import data/',
                'pubs list citekey:Page99',
                'pubs list key:eiNstein_1935',
                'pubs list --ignore-case key:eiNstein_1935',
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1, len(outs[2].splitlines()))
        self.assertEqual(0, len(outs[3].splitlines()))
        self.assertEqual(1, len(outs[4].splitlines()))

    def test_list_chronological_order(self):
        cmds = ['pubs init',
                'pubs import data/',
                'pubs remove -f Einstein_1935',
                'pubs remove -f Cesar2013',
                'pubs list --chronological',
                'pubs import bibexamples/noyear.bib',
                'pubs list -C',
                ]
        data_chrono_correct = '[Schrodinger_1935] Schrödinger, E. and Born, M. "Discussion of Probability Relations between Separated Systems" Mathematical Proceedings of the Cambridge Philosophical Society (1935) \n' \
                   '[turing1950computing] Turing, Alan M "Computing machinery and intelligence" Mind (1950) \n' \
                   '[Bell_1964] Bell, J. S. "On the Einstein Podolsky Rosen paradox" Physics Physique физика (1964) \n' \
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n' \
                   '[10.1371_journal.pone.0038236] Lyon, Caroline and Nehaniv, Chrystopher L. and Saunders, Joe "Interactive Language Learning by Robots: The Transition from Babbling to Word Forms" PLoS ONE (2012) \n' \
                   '[10.1371_journal.pone.0063400] Martius, Georg and Der, Ralf and Ay, Nihat "Information Driven Self-Organization of Complex Robotic Behaviors" PLoS ONE (2013) \n'
        correct = [ data_chrono_correct,
                   data_chrono_correct + '[Doe_noyear] Doe, John "About Assigning Timestamps to Research Articles" Journal Example \n'
                   ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(outs[4], correct[0])
        self.assertEqual(outs[6], correct[1])

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
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) | network, search\n' +
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


class TestURL(DataCommandTestCase):

    def setUp(self):
        super(TestURL, self).setUp()
        init = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add data/turing1950.bib',
                'pubs add data/martius.bib',
                ]
        self.execute_cmds(init)

    @mock.patch('webbrowser.open')
    def test_url_open_one(self, wb_open):
        cmds = ['pubs url Page99',
                ]
        correct = ['info: opening url http://ilpubs.stanford.edu:8090/422/\n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)

    @mock.patch('webbrowser.open')
    def test_url_open_missing(self, wb_open):
        cmds = [('pubs url turing1950computing', None, None, 'warning: turing1950computing has no url\n'),
                ]
        self.execute_cmds(cmds)

    @mock.patch('webbrowser.open')
    def test_url_open_multiple(self, wb_open):
        cmds = ['pubs url Page99 10.1371_journal.pone.0063400',
                ]
        correct = ['info: opening url http://ilpubs.stanford.edu:8090/422/\n' +
                   'info: opening url http://dx.doi.org/10.1371%2Fjournal.pone.0063400\n',
                   ]
        out = self.execute_cmds(cmds)
        self.assertEqual(out, correct)



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
                   'data/pagerank.pdf was copied to /paper_first/doc/Page99.pdf inside the pubs repository.\n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) [pdf] \n',
                   '\n',
                   '',
                   'network, search\n',
                   'info: Assuming search to be a tag.\n'
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) [pdf] | network, search\n',
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
                   'search, network\n',
                  ]

        cmds = ['pubs init -p paper_first/',
                'pubs add -d data/pagerank.pdf data/pagerank.bib',
                'pubs tag',
                'pubs tag Page99 network+search',
                'pubs tag',
               ]

        out = self.execute_cmds(cmds)

        def clean(s):
            return set(s.strip().split(', '))

        self.assertEqual(clean(correct[2]), clean(out[2]))
        self.assertEqual(clean(correct[4]), clean(out[4]))

    def test_conf(self):
        cmds = ['pubs init',
                ('pubs conf', [str_fixtures.sample_conf]),
               ]
        self.execute_cmds(cmds)
        self.assertFileContentEqual(os.path.expanduser('~/.pubsrc'),
                                    str_fixtures.sample_conf)

    def test_editor_aborts(self):
        with self.assertRaises(FakeSystemExit):
            cmds = ['pubs init',
                    'pubs add data/pagerank.bib',
                    ('pubs edit Page99', ['', 'n']),
                   ]
            self.execute_cmds(cmds)

    def test_editor_succeeds_on_second_edit(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ('pubs edit Page99', [
                    '@misc{Page99, title="TTT" author="X. YY"}', 'y',
                    '@misc{Page99, title="TTT", author="X. YY"}', '']),
                ('pubs list', [], '[Page99] YY, X. "TTT" \n')
                ]
        self.execute_cmds(cmds)

    def test_editor_excludes_bibtex_field(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ]
        self.execute_cmds(cmds)
        config = conf.load_conf()
        config['main']['exclude_bibtex_fields'] = ['author']
        conf.save_conf(config)
        cmds = [('pubs edit Page99', ['@misc{Page99, title="TTT", author="auth"}', 'n'])]
        self.execute_cmds(cmds)
        with FakeFileOpen(self.fs)(self.default_pubs_dir + '/bib/Page99.bib', 'r') as buf:
            out = endecoder.EnDecoder().decode_bibdata(buf.read())
        for bib in out.values():
            self.assertFalse('author' in bib)
            self.assertTrue('title' in bib)

    def test_add_aborts(self):
        with self.assertRaises(FakeSystemExit):
            cmds = ['pubs init',
                    ('pubs add New', ['']),
                   ]
            self.execute_cmds(cmds)

    def test_add_succeeds_on_second_edit(self):
        cmds = ['pubs init',
                ('pubs add', [
                    '', 'y',
                    '@misc{New, title="TTT", author="X. YY"}', '']),
                ('pubs list', [], '[New] YY, X. "TTT" \n')
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
        bib1 = re.sub(r'year = \{1999\}', 'year = {2007}', bib)
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
        line1 = re.sub('\n', '| AI, computer\n', line)

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

    def test_export_excludes_bibtex_field(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib'
                ]
        self.execute_cmds(cmds)
        config = conf.load_conf()
        config['main']['exclude_bibtex_fields'] = ['url']
        conf.save_conf(config)
        outs = self.execute_cmds(['pubs export Page99'])
        for bib in endecoder.EnDecoder().decode_bibdata(outs[0]).values():
            self.assertFalse('url' in bib)
            self.assertTrue('title' in bib and 'author' in bib)

    def test_import(self):
        cmds = ['pubs init',
                'pubs import data/',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(9, len(outs[-1].split('\n')))

    def test_import_one(self):
        cmds = ['pubs init',
                'pubs import data/ Page99',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_import_does_not_overwrite(self):
        with FakeFileOpen(self.fs)('data/real.bib', 'w') as f:
            f.write(str_fixtures.bibtex_external0)
        with FakeFileOpen(self.fs)('data/fake.bib', 'w') as f:
            f.write(str_fixtures.bibtex_external_alt)
        cmds = ['pubs init',
                'pubs import data/real.bib Page99',
                'pubs list',
                'pubs import data/fake.bib Page99',
                'pubs list',
               ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(outs[-3], outs[-1])


    def test_import_overwrites(self):
        cmds = ['pubs init',
                'pubs import data/ Page99',
                'pubs import --overwrite data/ Page99',
                'pubs list'
               ]

        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_import_fails_without_ignore(self):
        with FakeFileOpen(self.fs)('data/fake.bib', 'w') as f:
            f.write(str_fixtures.not_bibtex)
        cmds = ['pubs init',
                'pubs import data/ Page99',
                ]
        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

    def test_import_ignores(self):
        with FakeFileOpen(self.fs)('data/fake.bib', 'w') as f:
            f.write(str_fixtures.not_bibtex)
        cmds = ['pubs init',
                'pubs import --ignore-malformed data/ Page99',
                'pubs list'
                ]
        outs = self.execute_cmds(cmds)
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))

    def test_import_excludes_bibtex_field(self):
        self.execute_cmds(['pubs init'])
        config = conf.load_conf()
        config['main']['exclude_bibtex_fields'] = ['abstract']
        conf.save_conf(config)
        self.execute_cmds(['pubs import data/ Page99'])
        with FakeFileOpen(self.fs)(self.default_pubs_dir + '/bib/Page99.bib', 'r') as buf:
            out = endecoder.EnDecoder().decode_bibdata(buf.read())
        for bib in out.values():
            self.assertFalse('abstract' in bib)
            self.assertTrue('title' in bib and 'author' in bib)

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
                'pubs list -c ' + alt_conf,
               ]
        outs = self.execute_cmds(cmds)
        # check if pubs works as expected
        self.assertEqual(1 + 1, len(outs[-1].split('\n')))
        # check whether we actually changed the config file
        self.assertFalse(os.path.isfile(self.default_conf_path))
        self.assertTrue(os.path.isfile(alt_conf))

        with open(alt_conf, 'r') as fd:
            conf_text = fd.read()
        outs = self.execute_cmds([('pubs conf -c ' + alt_conf, conf_text)])


    def test_statistics(self):
        cmds = ['pubs init',
                'pubs statistics',
                'pubs add data/pagerank.bib',
                'pubs add -d data/turing-mind-1950.pdf data/turing1950.bib',
                'pubs add data/martius.bib',
                'pubs add data/10.1371%2Fjournal.pone.0038236.bib',
                'pubs tag Page99 A+B',
                'pubs tag turing1950computing C',
                'pubs statistics',
                ]
        out = self.execute_cmds(cmds)
        lines = out[1].splitlines()
        self.assertEqual(lines[0], 'Your pubs repository is empty.')
        lines = out[-1].splitlines()
        self.assertEqual(lines[0], 'Repository statistics:')
        self.assertEqual(lines[1], 'Total papers: 4, 1 (25%) have a document attached')
        self.assertEqual(lines[2], 'Total tags: 3, 2 (50%) of papers have at least one tag')

    def test_add_no_extension(self):
        """This tests checks that a paper which document has no extension does
        not raise issues when listing. This test might be removed if decided to
        prevent such documents. It would then need to be replaced by a check
        that this is prevented."""
        self.fs.add_real_file(os.path.join(self.rootpath, 'data', 'pagerank.pdf'),
                              target_path=os.path.join('data', 'no-ext'))
        correct = ['Initializing pubs in /pubs\n',
                   'added to pubs:\n[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
                   'data/no-ext was copied to /pubs/doc/Page99 inside the pubs repository.\n',
                   '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) [NOEXT] \n',
                  ]
        cmds = ['pubs init -p /pubs',
                'pubs add -d data/no-ext data/pagerank.bib',
                'pubs list',
               ]
        actual = self.execute_cmds(cmds, capture_output=True)
        self.assertEqual(correct, actual)

    def test_add_non_standard(self):
        """Test that non-standard bibtex are correctly added"""
        self.fs.add_real_directory(os.path.join(self.rootpath, 'data_non_standard'), read_only=False)
        correct = ['Initializing pubs in /pubs\n',
                   'added to pubs:\n[Geometric_phases]  "Geometric phases in physics" (1989) \n',
                   'added to pubs:\n[hadoop] Foundation, Apache Software "Hadoop" \n',
                  ]
        cmds = ['pubs init -p /pubs',
                'pubs add data_non_standard/non_standard_collection.bib',
                'pubs add data_non_standard/non_standard_software.bib',
                # 'pubs list',
               ]
        actual = self.execute_cmds(cmds, capture_output=True)
        self.assertEqual(correct, actual)


    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_readme(self, reqget):
        """Test that the readme example work."""
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/Loeb_2012.pdf')
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/oyama2000the.pdf')
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/Knuth1995.pdf')

        cmds = ['pubs init',
                'pubs import data/three_articles.bib',
                'pubs add data/pagerank.bib -d data/pagerank.pdf',
                #'pubs add -D 10.1007/s00422-012-0514-6 -d data/pagerank.pdf',
                'pubs add -X math/9501234 -d data/Knuth1995.pdf',
                'pubs add -D 10.1007/s00422-012-0514-6',
                'pubs doc add data/Loeb_2012.pdf Loeb_2012',
               ]
        self.execute_cmds(cmds, capture_output=True)

    @pytest.mark.skip(reason="isbn is not working anymore, see https://github.com/pubs/pubs/issues/276")
    @mock.patch('pubs.apis.requests.get', side_effect=mock_requests.mock_requests_get)
    def test_isbn(self, reqget):
        """Test that the readme example work."""
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/Loeb_2012.pdf')
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/oyama2000the.pdf')
        self.fs.add_real_file(os.path.join(self.rootpath, 'data/pagerank.pdf'), target_path='data/Knuth1995.pdf')

        cmds = ['pubs init',
                #'pubs add -D 10.1007/s00422-012-0514-6 -d data/pagerank.pdf',
                'pubs add -I 978-0822324669 -d data/oyama2000the.pdf',
               ]
        self.execute_cmds(cmds, capture_output=True)


    def test_ambiguous_citekey(self):
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                'pubs add data/pagerank.bib', # now we have Page99 and Page99a
                'pubs edit Page',
                ]
        output = '\n'.join(["error: Be more specific; 'Page' matches multiples citekeys:",
                            "    [Page99] Page, Lawrence et al. \"The PageRank Citation Ranking: Bringing Order to the Web.\" (1999) ",
                            "    [Page99a] Page, Lawrence et al. \"The PageRank Citation Ranking: Bringing Order to the Web.\" (1999) \n"])

        with self.assertRaises(FakeSystemExit):
            self.execute_cmds(cmds)

        self.assertEqual(self.captured_stderr, output)



@ddt.ddt
class TestCache(DataCommandTestCase):
    """\
    Run tests on fake filesystems supporting both integers and nanosecond
    stat times.
    """

    def setUp(self):
        pass

    def test_remove(self):
        DataCommandTestCase.setUp(self)
        cmds = ['pubs init',
                'pubs add data/pagerank.bib',
                ('pubs remove Page99', ['y']),
                'pubs list',
               ]
        out = self.execute_cmds(cmds)
        self.assertEqual(1, len(out[3].split('\n')))

    def test_edit(self):
        DataCommandTestCase.setUp(self)

        bib = str_fixtures.bibtex_external0
        bib1 = re.sub(r'year = \{1999\}', 'year = {2007}', bib)

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


class TestConfigChange(DataCommandTestCase):

    def test_max_authors_default(self):
        line_al   = '[Page99] Page, Lawrence et al. "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'
        line_full = '[Page99] Page, Lawrence and Brin, Sergey and Motwani, Rajeev and Winograd, Terry "The PageRank Citation Ranking: Bringing Order to the Web." (1999) \n'

        self.execute_cmds(['pubs init', 'pubs add data/pagerank.bib'])

        for max_authors in [1, 2, 3]:
            self.update_config({'main': {'max_authors': max_authors}})
            self.execute_cmds([('pubs list', None, line_al, None)])

        for max_authors in [-1, 0, 4, 5, 10]:
            self.update_config({'main': {'max_authors': max_authors}})
            self.execute_cmds([('pubs list', None, line_full, None)])



if __name__ == '__main__':
    unittest.main(verbosity=2)
