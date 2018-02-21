from __future__ import (print_function, absolute_import, division,
                        unicode_literals)

import copy

try:
    import bibtexparser as bp
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
    record = bp.customization.journal(record)
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

    def _entry_to_bp_entry(self, key, entry, ignore_fields=[]):
        """Convert back entries to the format expected by bibtexparser."""
        entry[BP_ID_KEY] = key
        # Convert internal 'type' to bibtexparser entrytype key
        entry[BP_ENTRYTYPE_KEY] = entry.pop(TYPE_KEY)
        for f in ignore_fields:
            entry.pop(f, None)
        if 'author' in entry:
            entry['author'] = ' and '.join(
                author for author in entry['author'])
        if 'editor' in entry:
            entry['editor'] = ' and '.join(
                editor['name'] for editor in entry['editor'])
        if 'journal' in entry:
            entry['journal'] = entry['journal']['name']
        if 'keyword' in entry:
            entry['keyword'] = ', '.join(
                keyword for keyword in entry['keyword'])
        return entry

    def decode_bibdata(self, bibdata):
        """"""
        try:
            try:
                entries = bp.bparser.BibTexParser(
                    bibdata, homogenize_fields=True,
                    customization=customizations).get_entry_dict()
            except TypeError:
                entries = bp.bparser.BibTexParser(
                    bibdata,
                    customization=customizations).get_entry_dict()

            # Remove id from bibtexparser attribute which is stored as citekey
            for e in entries:
                entries[e].pop(BP_ID_KEY)
                # Convert bibtexparser entrytype key to internal 'type'
                t = entries[e].pop(BP_ENTRYTYPE_KEY)
                entries[e][TYPE_KEY] = t
            if len(entries) > 0:
                return entries
        except Exception:
            import traceback
            traceback.print_exc()
        raise ValueError('could not parse provided bibdata:\n{}'.format(bibdata))
