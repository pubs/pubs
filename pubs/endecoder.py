from __future__ import absolute_import, unicode_literals

import copy
import logging

# both needed to intercept exceptions.
import pyparsing
import bibtexparser

try:
    import bibtexparser as bp
    # don't let bibtexparser display stuff
    bp.bparser.logger.setLevel(level=logging.CRITICAL)
except ImportError:
    print("error: you need to install bibterxparser; try running 'pip install "
          "bibtexparser'.")
    exit(-1)

import yaml

from .bibstruct import TYPE_KEY

"""Important notice:
    All functions and methods in this file assume and produce unicode data.
"""


if bp.__version__ > "0.6.0":
    BP_ID_KEY = 'ID'
    BP_ENTRYTYPE_KEY = 'ENTRYTYPE'
else:
    BP_ID_KEY = 'id'
    BP_ENTRYTYPE_KEY = 'type'


BIBFIELD_ORDER = ['author', 'title', 'journal', 'institution', 'publisher',
                  'year', 'month', 'number', 'volume', 'pages', 'url', 'link',
                  'doi', 'note', 'abstract']



class BibDecodingError(Exception):

    def __init__(self, error_msg, bibdata):
        """
        :param error_msg: specific message about what went wrong
        :param bibdata:   the data that was unsuccessfully decoded.
        """
        super(Exception, self).__init__(error_msg)  # make `str(self)` work.
        self.data = bibdata


class EmptyData(BibDecodingError):

    def __init__(self, bibstr, msg):
        self.bibstr, self.msg = bibstr, msg

    def print(self, ui):
        ui.error(self.msg)

class SyntaxError(BibDecodingError):

    def __init__(self, bibstr, pybtex_exc):
        self.bibstr, self.pybtex_exc = bibstr, pybtex_exc

    def print(self, ui, context_margin=3):
        """
        Print the syntax error.

        :param context_margin:  how much line to display around the problematic line
        """
        exc = self.pybtex_exc
        lines = self.bibstr.split('\n')
        ui.error('bibtex syntax error at line {}: {}'.format(exc.lineno, exc.args[0]))

        n_digit = math.floor(math.log10(len(lines))+1)
        line_prefix = 'L{:' + str(n_digit) + 'd}: {}'
        for i, line in enumerate(lines[max(0, exc.lineno-context_margin-1): exc.lineno-1]):
            lineno = max(0, exc.lineno-context_margin) + i
            ui.message(line_prefix.format(lineno, line))
        context_lines = e.get_context().split('\n')
        for i, line in enumerate(context_lines):
            if i == 0:
                ui.message(line_prefix.format(exc.lineno, line))
            else:
                ui.message(' ' + n_digit*'.' + '   ' + line)
        for i, line in enumerate(lines[e.lineno+1:min(len(lines), e.lineno + context_margin + 1)]):
            lineno = e.lineno + 1 + i
            ui.message(line_prefix.format(lineno, line))


def sanitize_citekey(record):
    record[BP_ID_KEY] = record[BP_ID_KEY].strip('\n')
    return record


def customizations(record):
    """ Use some functions delivered by the library

        :param record: a record
        :returns: -- customized record
    """

    # record = bp.customization.convert_to_unicode(record) # transform \& into & ones, messing-up latex
    record = bp.customization.type(record)
    record = bp.customization.author(record)
    record = bp.customization.editor(record)
    record = bp.customization.keyword(record)
    record = bp.customization.page_double_hyphen(record)

    record = sanitize_citekey(record)

    return record


class EnDecoder(object):
    """ Encode and decode content.

        Design choices:
        * Has no interaction with disk.
        * Incoming content is not trusted.
        * Returned content must be correctly formatted (no one else checks).
        * Failures raise ValueError
        * encode_bibdata will try to recognize exceptions
    """

    class BibDecodingError(Exception):

        def __init__(self, error_msg, bibdata):
            """
            :param error_msg: specific message about what went wrong
            :param bibdata:   the data that was unsuccessfully decoded.
            """
            super(Exception, self).__init__(error_msg)  # make `str(self)` work.
            self.data = bibdata

    bwriter = bp.bwriter.BibTexWriter()
    bwriter.display_order = BIBFIELD_ORDER

    def encode_metadata(self, metadata):
        return yaml.safe_dump(metadata, allow_unicode=True,
                              encoding=None, indent=4)

    def decode_metadata(self, metadata_raw):
        return yaml.safe_load(metadata_raw)

    def encode_bibdata(self, bibdata, ignore_fields=[]):
        """Encode bibdata """
        
        bpdata = bp.bibdatabase.BibDatabase()
        bpdata.entries = [self._entry_to_bp_entry(k, copy.copy(bibdata[k]),
                                                  ignore_fields=ignore_fields)
                          for k in bibdata]
        return self.bwriter.write(bpdata)

    # def _entry_to_bp_entry(self, key, entry, ignore_fields=[]):
    #     """Convert back entries to the format expected by bibtexparser."""
    #     entry[BP_ID_KEY] = key
    #     # Convert internal 'type' to bibtexparser entrytype key
    #     entry[BP_ENTRYTYPE_KEY] = entry.pop(TYPE_KEY)
    #     for f in ignore_fields:
    #         entry.pop(f, None)
    #     if 'author' in entry:
    #         entry['author'] = ' and '.join(
    #             author for author in entry['author'])
    #     if 'editor' in entry:
    #         entry['editor'] = ' and '.join(
    #             editor for editor in entry['editor'])
    #     if 'keyword' in entry:
    #         entry['keyword'] = ', '.join(
    #             keyword for keyword in entry['keyword'])
    #     return entry


    def decode_bibdata(self, bibstr):
        """Decodes bibdata from string.

        If the decoding fails, returns a BibDecodingError, either EmptyData or SyntaxError.
        """
        bibstr = bibstr.strip()  # remove leading and trailing spaces
        if len(bibstr) == 0:
            error_msg = 'the provided string has no content.'
            raise EmtpyData(error_msg, bibstr)
        try:
            entries = pybtex.database.parse_string(bibstr).entries
            if len(entries) > 0:
                return entries
            else:
                error_msg = 'no valid entry found in the provided data:\n{}'.format(bibstr)
                raise EmptyData(error_msg, bibstr)
        except pybtex.parser.SyntaxError as exc:
            raise SyntaxError(bibstr, exc)
