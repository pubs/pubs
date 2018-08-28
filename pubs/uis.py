from __future__ import print_function, unicode_literals

import os
import sys
import shlex
import locale
import codecs
import tempfile
import traceback
import subprocess

from . import color
from . import config
from .p3 import _get_raw_stdout, _get_raw_stderr, input, ustr
from .content import check_file, read_text_file, write_file


DEBUG = False  # unhandled exceptions traces are printed
DEBUG_ALL_TRACES = False  # handled exceptions traces are printed
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

    Use vi as a default.
    """
    return os.environ.get('EDITOR', 'vi')


def get_ui():
    if _ui is None:
        return PrintUI(config.load_default_conf())  # no editor support. (#FIXME?)
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
        print('{}: {}'.format(color.dye_out('info', 'ok'), message), **kwargs)

    def warning(self, message, **kwargs):
        kwargs['file'] = self._stderr
        print('{}: {}'.format(color.dye_err('warning', 'warning'), message), **kwargs)

    def error(self, message, **kwargs):
        kwargs['file'] = self._stderr
        print('{}: {}'.format(color.dye_err('error', 'error'), message), **kwargs)

        if DEBUG_ALL_TRACES:  # if an exception has been raised, print the trace.
            if sys.exc_info()[0] is not None:
                traceback.print_exception(*sys.exc_info())

    def exit(self, error_code=1):
        sys.exit(error_code)

    def handle_exception(self, exc):
        """Attempts to handle exception.

        :returns: True if exception has been handled (currently never happens)
        """
        self.error(ustr(exc))
        if DEBUG or self.debug:
            raise
        else:
            self.exit()
        return True # never happens


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
            self.error('Standard input ended while waiting for answer.')
            self.exit(1)
        return ustr(data)  #.decode('utf-8')

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

        option_str = '/'.join(["{}{}".format(color.dye_out(c, 'bold'), s[1:])
                               for c, s in zip(displayed_chars, options)])

        self.message('{}: {} {}: '.format(color.dye_err('prompt', 'warning'), question, option_str), end='')
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
            self.message('Incorrect option.', option_str)

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
            self.message('Incorrect option.', option_str)

    def input_yn(self, question='', default='y'):
        d = 0 if default in (True, 'y', 'yes') else 1
        answer = self.input_choice_ng(['yes', 'no'], default=d, question=question)
        return [True, False][answer]

    def editor_input(self, initial="", suffix='.tmp'):
        """Use an editor to get input"""
        str_initial = initial.encode('utf-8')  # TODO: make it a configuration item
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            tfile_name = temp_file.name
            temp_file.write(str_initial)
        self._call_editor(tfile_name)
        content = read_text_file(tfile_name)
        os.remove(tfile_name)
        return content

    def edit_file(self, path, temporary):
        if temporary:
            check_file(path, fail=True)
            content = read_text_file(path)
            content = self.editor_input(content)
            write_file(path, content)
        else:
            self._call_editor(path)

    def _call_editor(self, path):
        """Call the editor, and checks that no error were raised by the OS"""
        cmd = shlex.split(self.editor)  # this enable editor command with option, e.g. gvim -f
        cmd.append(path)
        try:
            subprocess.call(cmd)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                self.error(("Error while calling editor '{}'. The editor may "
                            "not be present. You can change the text editor "
                            "that pubs uses by setting the $EDITOR environment "
                            "variable, or by running `pubs conf` and setting "
                            "the `edit_cmd` field."
                            ).format(self.editor))
                # handle file not found error.
                self.exit()
            else:
                # Something else went wrong while trying to run `wget`
                self.handle_exception(e)
