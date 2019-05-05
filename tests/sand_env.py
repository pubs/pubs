from __future__ import print_function, unicode_literals

import os
import sys
import shutil
import tempfile
import unittest

import six

from pubs import pubs_cmd, color, content, uis, p3
from pubs.config import conf
from pubs.p3 import _fake_stdio, _get_fake_stdio_ucontent


# makes the tests very noisy
PRINT_OUTPUT   = True
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


# capture output

def capture(f, verbose=False):
    """Capture the stdout and stderr output.

    Useful for comparing the output with the expected one during tests.

    :param f:        The function to capture output from.
    :param verbose:  If True, print call will still display their outputs.
                     If False, they will be silenced.

    """
    def newf(*args, **kwargs):
        old_stderr, old_stdout = sys.stderr, sys.stdout
        sys.stdout = _fake_stdio(additional_out=old_stderr if verbose else None)
        sys.stderr = _fake_stdio(additional_out=old_stderr if False else None)
        try:
            return f(*args, **kwargs), _get_fake_stdio_ucontent(sys.stdout), _get_fake_stdio_ucontent(sys.stderr)
        finally:
            sys.stderr, sys.stdout = old_stderr, old_stdout
    return newf


# scriptable input

class FakeInput():
    """ Replace the input() command, and mock user input during tests

        Instanciate as :
        input = FakeInput(['yes', 'no'])
        then replace the input command in every module of the package :
        input.as_global()
        Then :
        input() returns 'yes'
        input() returns 'no'
        input() raises IndexError
     """

    class UnexpectedInput(Exception):
        pass

    def __init__(self, inputs, module_list=tuple()):
        self.inputs = list(inputs) or []
        self.module_list = module_list
        self._cursor = 0

    def as_global(self):
        for md in self.module_list:
            md.input = self
            if md.__name__ == 'pubs.uis':
                md.InputUI.editor_input = self
                md.InputUI.edit_file = self.input_to_file

                # Do not catch UnexpectedInput
                original_handler = md.InputUI.handle_exception

                def handler(ui, exc):
                    if isinstance(exc, self.UnexpectedInput):
                        raise
                    else:
                        original_handler(ui, exc)

                md.InputUI.handle_exception = handler

    def input_to_file(self, path_to_file, temporary=True):
        content.write_file(path_to_file, self())

    def add_input(self, inp):
        self.inputs.append(inp)

    def __call__(self, *args, **kwargs):
        try:
            inp = self.inputs[self._cursor]
            self._cursor += 1
            return inp
        except IndexError:
            raise self.UnexpectedInput('Unexpected user input in test.')


class SandboxedCommandTestCase(unittest.TestCase):

    maxDiff = 1000000

    def setUp(self):
        super(SandboxedCommandTestCase, self).setUp()
        self.temp_dir = tempfile.mkdtemp()
        self.default_pubs_dir  = os.path.join(self.temp_dir, 'pubs')
        self.default_conf_path = os.path.join(self.temp_dir, 'pubsrc')
        os.chdir(os.path.dirname(__file__))

    @staticmethod
    def _normalize(s):
        """Normalize a string for robust comparisons."""
        s = color.undye(s)
        try:
            s = s.decode('utf-8')
        except AttributeError:
            pass
        return s

    def _compare_output(self, s1, s2):
        if s1 is not None and s2 is not None:
            return self.assertEqual(self._normalize(s1), self._normalize(s2))

    def _preprocess_cmd(self, cmd):
        """Sandbox the pubs command into a temporary directory"""
        cmd_chunks = cmd.split(' ')
        assert cmd_chunks[0] == 'pubs'
        prefix = ['pubs', '-c', self.default_conf_path]
        if cmd_chunks[1] == 'init':
            return ' '.join(prefix + ['init', '-p', self.default_pubs_dir] + cmd_chunks[2:])
        else:
            return ' '.join(prefix + cmd_chunks[1:])

    def execute_cmds(self, cmds, capture_output=CAPTURE_OUTPUT):
        """ Execute a list of commands, and capture their output

        A command can be a string, or a tuple of size 2, 3 or 4.
        In the latter case, the command is :
        1. a string reprensenting the command to execute
        2. the user inputs to feed to the command during execution
        3. the expected output on stdout, verified with assertEqual.
        4. the expected output on stderr, verified with assertEqual. (this does not work yet)
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
                actual_cmd = self._preprocess_cmd(actual_cmd)
                # Always set fake input: test should not ask unexpected user input
                input = FakeInput(inputs, [content, uis, p3])
                input.as_global()
                try:
                    if capture_output:
                        execute_captured = capture(pubs_cmd.execute, verbose=PRINT_OUTPUT)
                        _, stdout, stderr = execute_captured(actual_cmd.split())
                        self._compare_output(stdout, expected_out)
                        self._compare_output(stderr, expected_err)
                        outs.append(self._normalize(stdout))
                    else:
                        pubs_cmd.execute(actual_cmd.split())
                except FakeInput.UnexpectedInput:
                    self.fail('Unexpected input asked by command: {}.'.format(actual_cmd))
            return outs
        except SystemExit as exc:
            exc_class, exc, tb = sys.exc_info()
            if sys.version_info.major == 2:
                # using six to avoid a SyntaxError in Python 3.x
                six.reraise(FakeSystemExit, FakeSystemExit(*exc.args), tb)
            else:
                raise FakeSystemExit(*exc.args).with_traceback(tb)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)



    ## Testing the test environments


class TestInput(unittest.TestCase):
    """Test that the fake input mechanisms work correctly in the tests"""

    def test_input(self):
        input = FakeInput(['yes', 'no'])
        self.assertEqual(input(), 'yes')
        self.assertEqual(input(), 'no')
        with self.assertRaises(FakeInput.UnexpectedInput):
            input()

    def test_input2(self):
        other_input = FakeInput(['yes', 'no'], module_list=[color])
        other_input.as_global()
        self.assertEqual(color.input(), 'yes')
        self.assertEqual(color.input(), 'no')
        with self.assertRaises(FakeInput.UnexpectedInput):
            color.input()

    def test_editor_input(self):
        sample_conf = conf.load_default_conf()
        ui = uis.InputUI(sample_conf)

        other_input = FakeInput(['yes', 'no'], module_list=[uis])
        other_input.as_global()
        self.assertEqual(ui.editor_input('fake_editor'), 'yes')
        self.assertEqual(ui.editor_input('fake_editor'), 'no')
        with self.assertRaises(FakeInput.UnexpectedInput):
            ui.editor_input()


class TestSandboxedCommandTestCase(SandboxedCommandTestCase):

    def test_init_add(self):
        """Simple init and add example"""
        correct = ("added to pubs:\n"
                   "[Page99] Page, Lawrence et al. \"The PageRank Citation Ranking: Bringing Order to the Web.\" (1999) \n")
        cmds = ['pubs init',
                ('pubs add data/pagerank.bib', [], correct),
                ('pubs add abc', [], '', 'error: File does not exist: /Users/self/Volumes/ResearchSync/projects/pubs/abc\n')
               ]
        self.execute_cmds(cmds)



if __name__ == '__main__':
    unittest.main(verbosity=2)
