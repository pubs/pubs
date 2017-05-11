from __future__ import print_function

import os
import sys
import locale
import codecs

from .content import editor_input
from . import color
from . import config
from .p3 import _get_raw_stdout, _get_raw_stderr, input, ustr


# package-shared ui that can be accessed using :
# from uis import get_ui
# ui = get_ui()
# you must instanciate ui with a Config instance using init_ui(config)
_ui = None


def _get_encoding(conf):
    """Get local terminal encoding or user preference in config."""
    enc = 'utf-8'
    try:
        enc = locale.getdefaultlocale()[1]
    except ValueError:
        pass  # Keep default
    if conf is None:
        return enc or 'utf-8'
    return conf.get('terminal-encoding', enc or 'utf-8')


def _get_local_editor():
    """Get the editor from environment variables.

    Use nano as a default.
    """
    return os.environ.get('EDITOR', 'nano')


def get_ui():
    if _ui is None:
        return PrintUI(config.load_default_conf()) # no editor support. (#FIXME?)
    return _ui


def init_ui(conf, force_colors=False):
    global _ui
    _ui = InputUI(conf, force_colors=force_colors)


class PrintUI(object):

    def __init__(self, conf, force_colors=False):
        """
        :param conf: if None, conservative default values are used.
                     Useful to instanciate the UI before parsing the config file.
        """
        color.setup(conf, force_colors=force_colors)
        self.encoding = _get_encoding(conf)
        self._stdout  = codecs.getwriter(self.encoding)(_get_raw_stdout(),
                                                        errors='replace')
        self._stderr  = codecs.getwriter(self.encoding)(_get_raw_stderr(),
                                                        errors='replace')
        self.debug = conf['main'].get('debug', False)

    def message(self, *messages, **kwargs):
        kwargs['file'] = self._stdout
        print(*messages, **kwargs)

    def info(self, message, **kwargs):
        kwargs['file'] = self._stdout
        print(u'{}: {}'.format(color.dye_out('info', 'ok'), message), **kwargs)

    def warning(self, message, **kwargs):
        kwargs['file'] = self._stderr
        print(u'{}: {}'.format(color.dye_err('warning', 'warning'), message), **kwargs)

    def error(self, message, **kwargs):
        kwargs['file'] = self._stderr
        print(u'{}: {}'.format(color.dye_err('error', 'error'), message), **kwargs)

    def exit(self, error_code=1):
        sys.exit(error_code)

    def handle_exception(self, exc):
        """Attempts to handle exception.

        :returns: True if exception has been handled (currently never happens)
        """
        if not self.debug:
            self.error(ustr(exc))
            self.exit()
        return False


class InputUI(PrintUI):
    """UI class. Stores configuration parameters and system information.
    """

    def __init__(self, conf, force_colors=False):
        super(InputUI, self).__init__(conf, force_colors=force_colors)
        self.editor = conf['main']['edit_cmd'] or _get_local_editor()

    def input(self):
        try:
            data = input()
        except EOFError:
            self.error(u'Standard input ended while waiting for answer.')
            self.exit(1)
        return ustr(data) #.decode('utf-8')

    def input_choice_ng(self, options, option_chars=None, default=None, question=''):
        """Ask the user to chose between a set of options. The user is asked
        to input a char corresponding to the option he chooses.

        :param options: list of strings
            list of options
        :param default: int
            default if no option is accepted, if None answer is required
        :param question: string
        :returns: int
            the index of the chosen option
        """
        option_chars = [s[0] for s in options]
        displayed_chars = [c.upper() if i == default else c
                           for i, c in enumerate(option_chars)]

        if len(set(option_chars)) != len(option_chars): # duplicate chars, char choices are deactivated. #FIXME: should only deactivate ambiguous chars
            option_chars = []

        option_str = u'/'.join(["{}{}".format(color.dye_out(c, 'bold'), s[1:])
                               for c, s in zip(displayed_chars, options)])

        self.message(u'{}: {} {}: '.format(color.dye_err('prompt', 'warning'), question, option_str), end='')
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
            self.message(u'Incorrect option.', option_str)


    def input_choice(self, options, option_chars, default=None, question=''):
        """Ask the user to chose between a set of options. The user is asked
        to input a char corresponding to the option he chooses.

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
        self.message(question, option_str)
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
            self.message(u'Incorrect option.', option_str)

    def input_yn(self, question='', default='y'):
        d = 0 if default in (True, 'y', 'yes') else 1
        answer = self.input_choice_ng(['yes', 'no'], default=d, question=question)
        return [True, False][answer]

    def editor_input(self, initial="", suffix='.tmp'):
        return editor_input(self.editor, initial=initial, suffix=suffix)
