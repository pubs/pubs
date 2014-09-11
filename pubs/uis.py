from __future__ import print_function

import sys
import locale
import codecs

from .content import editor_input
from . import color
from .p3 import _get_raw_stdout


# package-shared ui that can be accessed using :
# from uis import get_ui
# ui = get_ui()
# you must instanciate ui with a Config instance using init_ui(config)
_ui = None


def _get_encoding(config):
    """Get local terminal encoding or user preference in config."""
    enc = None
    try:
        enc = locale.getdefaultlocale()[1]
    except ValueError:
        pass  # Keep default
    return config.get('terminal-encoding', enc or 'utf8')


def get_ui():
    if _ui is None:
        raise ValueError('ui not instanciated yet')
    return _ui


def init_ui(config):
    global _ui
    _ui = UI(config)


class UI:
    """UI class. Stores configuration parameters and system information.
    """

    def __init__(self, config):
        color.setup(config.color)
        self.editor = config.edit_cmd
        self.encoding = _get_encoding(config)
        self._stdout = codecs.getwriter(self.encoding)(_get_raw_stdout(),
                                                       errors='replace')

    def print_(self, *strings):
        """Like print, but rather than raising an error when a character
        is not in the terminal's encoding's character set, just silently
        replaces it.
        """
        print(' '.join(strings), file=self._stdout)

    def input(self):
        try:
            data = input()
        except EOFError:
            self.error('Standard input ended while waiting for answer.')
            self.exit(1)
        return data

    def input_choice(self, options, option_chars, default=None, question=''):
        """Ask the user to chose between a set of options. The iser is asked
        to input a char corresponding to the option he choses.

        :param options: list of strings
            list of options
        :param option_chars: list of chars
            chars used to identify options, should be lowercase and not
            contain duplicates
        :param default: int
            default if no option is accepted, if None answer is required
        :param question: string
        :returns: int
            the index of the chosen option
        """
        displayed_chars = [s.upper() if i == default else s
                           for i, s in enumerate(option_chars)]
        option_str = ', '.join(["[%s]%s" % (color.dye(c, color.cyan), o)
                                for c, o in zip(displayed_chars, options)])
        self.print_(question, option_str)
        while True:
            answer = self.input()
            if answer is None or answer == '':
                if default is not None:
                    return default
            else:
                try:
                    return option_chars.index(answer.lower())
                except ValueError:
                    pass
            self.print_('Incorrect option.', option_str)

    def input_yn(self, question='', default='y'):
        d = 0 if default in (True, 'y', 'yes') else 1
        return (True, False)[self.input_choice(['yes', 'no'], ['y', 'n'],
                                               default=d, question=question)]

    def exit(self, error_code=1):
        sys.exit(error_code)

    def error(self, message):
        self.print_("%s: %s" % (color.dye('error', color.red), message))

    def warning(self, message):
        self.print_("%s: %s" % (color.dye('warning', color.yellow), message))

    def editor_input(self, initial="", suffix='.tmp'):
        return editor_input(self.editor, initial=initial, suffix=suffix)
