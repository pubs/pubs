# -*- coding: utf-8 -*-
"""Test appending a note file from the command-line using the '-a' arg"""

# If you store your pubs in a directory other than home, you may want to
# set this prior to running this test:
#   export PUBSCONF=~/.pubsrc

# vim -p tests/test_note_append.py tests/test_usecase.py

from __future__ import print_function, unicode_literals

import unittest
import os

from tests.test_usecase import DataCommandTestCase


class TestNoteAppend(DataCommandTestCase):
    """Test appending a note file from the command-line using the '-a' arg"""

    def setUp(self):
        """Initialize a bib entry containing citation key, Page99, for testing"""
        super(TestNoteAppend, self).setUp()
        init = ['pubs init',
                'pubs add data/pagerank.bib',
               ]
        self.execute_cmds(init)
        self.note_dir = os.path.join(self.default_pubs_dir, 'notes')

    def test_note_append(self):
        """Test appending the note file using the command-line argument, -a"""
        fin_notes = os.path.join(self.note_dir, 'Page99.txt')
        # Test adding first line
        cmds = [('pubs note Page99 -a aaa')]
        self.execute_cmds(cmds)
        note_lines = ['aaa']
        self.assertFileContentEqual(fin_notes, self._get_note_content(note_lines))
        # Test adding additional line
        cmds = [('pubs note Page99 -a bbb')]
        self.execute_cmds(cmds)
        note_lines.append('bbb')
        self.assertFileContentEqual(fin_notes, self._get_note_content(note_lines))

        # https://github.com/pubs/pubs/pull/201#discussion_r307499310
        # Test multiword line.
        #   * Pass the command split into a command and its args to
        #     execute_cmdsplit, which is called by execute_cmds:
        cmd_split = ['pubs', 'note', 'Page99', '-a', 'xxx yyy']
        self.execute_cmd_capture(cmd_split, expected_out=None, expected_err=None)
        note_lines.append('xxx yyy')
        self.assertFileContentEqual(fin_notes, self._get_note_content(note_lines))

    def test_note_append_unicode(self):
        fin_notes = os.path.join(self.note_dir, 'Page99.txt')
        # https://github.com/pubs/pubs/pull/201#discussion_r305274071
        # Test adding Chinese characters
        cmds = [('pubs note Page99 -a \347\350\346\345')]
        self.execute_cmds(cmds)
        note_lines = ['\347\350\346\345']
        self.assertFileContentEqual(fin_notes, self._get_note_content(note_lines))
        # Test adding Japanese character
        cmds = [('pubs note Page99 -a ソ')]
        self.execute_cmds(cmds)
        note_lines.append('ソ')
        self.assertFileContentEqual(fin_notes, self._get_note_content(note_lines))

    @staticmethod
    def _get_note_content(note_lines):
        """Given a list of note lines, return full note file content"""
        return '{lines}\n'.format(lines='\n'.join(note_lines))


if __name__ == '__main__':
    unittest.main(verbosity=2)
