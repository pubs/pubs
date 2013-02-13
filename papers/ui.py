from beets_ui import _encoding, input_

from color import colored


class UI:
    """UI class. Stores configuration parameters and system information.
    """

    def __init__(self, config):
        self.encoding = _encoding(config)
        self.color = config.getboolean('papers', 'color')

    def colored(self, s, *args, **kwargs):
        if self.color:
            return colored(s, *args, **kwargs)
        else:
            return s

    def print_(self, *strings):
        """Like print, but rather than raising an error when a character
        is not in the terminal's encoding's character set, just silently
        replaces it.
        """
        txt = [s.encode(self.encoding, 'replace')
                if isinstance(s, unicode) else s
               for s in strings]
        print(' '.join(txt))

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
        option_str = ', '.join(["[%s]%s" % (self.colored(c, 'cyan'), o)
                                for c, o in zip(displayed_chars, options)])
        self.print_(question, option_str)
        while True:
            answer = input_()
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
