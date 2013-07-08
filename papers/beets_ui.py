# This file contains functions taken from the user interface of the beet
# tool (http://beets.radbox.org).
#
# Copyright 2013, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.


import locale
import sys

from . import p3
from p3 import input


class UserError(Exception):
    """UI exception. Commands should throw this in order to display
    nonrecoverable errors to the user.
    """
    pass


def _encoding(config):
    """Tries to guess the encoding used by the terminal."""
    # Configured override?
    # Determine from locale settings.
    try:
        default_enc = locale.getdefaultlocale()[1] or 'utf8'
    except ValueError:
        # Invalid locale environment variable setting. To avoid
        # failing entirely for no good reason, assume UTF-8.
        default_enc = 'utf8'
    return config.get('terminal-encoding', default_enc)


def input_():
    """Get input and decodes the result to a Unicode string.
    Raises a UserError if stdin is not available. The prompt is sent to
    stdout rather than stderr. A printed between the prompt and the
    input cursor.
    """
    # raw_input incorrectly sends prompts to stderr, not stdout, so we
    # use print() explicitly to display prompts.
    # http://bugs.python.org/issue1927
    try:
        resp = input()
    except EOFError:
        raise UserError('stdin stream ended while input required')
    return resp.decode(sys.stdin.encoding or 'utf8', 'ignore')
