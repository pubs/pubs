from __future__ import print_function

import sys
import locale
import codecs

from .content import editor_input
from . import color
from .p3 import _get_raw_stdout, _get_raw_stderr, input


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
    return config.get('terminal-encoding', enc or 'utf-8')


def get_ui():
    if _ui is None:
        raise ValueError('ui not instanciated yet')
    return _ui


def init_ui(config):
    global _ui
    _ui = InputUI(config)


class PrintUI(object):

    def __init__(self, config):
        color.setup(config.color)
        self.encoding = _get_encoding(config)
        self._stdout  = codecs.getwriter(self.encoding)(_get_raw_stdout(),
                                                        errors='replace')
        self._stderr  = codecs.getwriter(self.encoding)(_get_raw_stderr(),
                                                        errors='replace')

    def print_out(self, *strings, **kwargs):
        """Like print, but rather than raising an error when a character
        is not in the terminal's encoding's character set, just silently
        replaces it.
        """
        print(' '.join(strings), file=self._stdout, **kwargs)

    def print_err(self, *strings, **kwargs):
        """Like print, but rather than raising an error when a character
        is not in the terminal's encoding's character set, just silently
        replaces it.
        """
        print(' '.join(strings), file=self._stderr, **kwargs)

    def error(self, message):
        self.print_err('{}: {}'.format(color.dye_err('error', 'red'), message))


    def warning(self, message):
        self.print_err("%s: %s" % (color.dye_err('warning', 'yellow'), message))



class InputUI(PrintUI):
    """UI class. Stores configuration parameters and system information.
    """

    def __init__(self, config):
        super(InputUI, self).__init__(config)
        self.editor = config.edit_cmd

    def exit(self, error_code=1):
        sys.exit(error_code)

    def input(self):
        try:
            data = input()
        except EOFError:
            self.error(u'Standard input ended while waiting for answer.')
            self.exit(1)
        return data.decode('utf-8')

    def input_choice_ng(self, options, option_chars=None, default=None, question=''):
        """Ask the user to chose between a set of options. The iser is asked
        to input a char corresponding to the option he choses.

        :param options: list of strings
            list of options
        :param default: int
            default if no option is accepted, if None answer is required
        :param question: string
        :returns: int
            the index of the chosen option
        """
        char_color = 'bold'
        option_chars = [s[0] for s in options]
        displayed_chars = [c.upper() if i == default else c
                           for i, c in enumerate(option_chars)]

        if len(set(option_chars)) != len(option_chars): # duplicate chars, char choices are deactivated. #FIXME: should only deactivate ambiguous chars
            option_chars = []
            char_color = color.end

        option_str = '/'.join(["{}{}".format(color.dye_out(c, 'bold'), s[1:])
                                for c, s in zip(displayed_chars, options)])

        self.print_out('{} {}: '.format(question, option_str), end='')
        while True:
            answer = self.input()
            if answer is None or answer == '':
                if default is not None:
                    return default
            else:
                try:
                    return options.index(answer.lower())
                except ValueError:
                    try: # FIXME options handling !!!
                        return option_chars.index(answer.lower())
                    except ValueError:
                        pass
            self.print_out('Incorrect option.', option_str)


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
        option_str = ', '.join(["[%s]%s" % (color.dye_out(c, 'cyan'), o)
                                for c, o in zip(displayed_chars, options)])
        self.print_out(question, option_str)
        while True:
            answer = self.input()
            if answer is None or answer == '':
                if default is not None:
                    return default
            else:
                try: # FIXME options handling !!!
                    return option_chars.index(answer.lower())
                except ValueError:
                    pass
            self.print_out('Incorrect option.', option_str)

    def input_yn(self, question='', default='y'):
        d = 0 if default in (True, 'y', 'yes') else 1
        answer = self.input_choice_ng(['yes', 'no'], default=d, question=question)
        return [True, False][answer]

    def editor_input(self, initial="", suffix='.tmp'):
        return editor_input(self.editor, initial=initial, suffix=suffix)
