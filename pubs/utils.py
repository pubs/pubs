# Functions here may belong somewhere else. In the mean time...
from __future__ import unicode_literals

import re

from . import color
from . import pretty


def resolve_citekey(repo, citekey, ui=None, exit_on_fail=True):
    """Check that a citekey exists, or autocompletes it if not ambiguous.
        :returns found citekey
    """
    # FIXME. Make me optionally non ui interactive/exiting
    citekeys = repo.citekeys_from_prefix(citekey)
    if len(citekeys) == 0:
        if ui is not None:
            ui.error("No citekey named or beginning with '{}'".format(
                     color.dye_out(citekey, 'citekey')))
            if exit_on_fail:
                ui.exit()
    elif len(citekeys) == 1:
        if citekeys[0] != citekey:
            if ui is not None:
                ui.info("'{}' has been autocompleted into '{}'.".format(
                        color.dye_out(citekey, 'citekey'),
                        color.dye_out(citekeys[0], 'citekey')))
            citekey = citekeys[0]
    elif citekey not in citekeys:
        if ui is not None:
            citekeys = sorted(citekeys)
            ui.error("Be more specific; '{}' matches multiples "
                     "citekeys:".format(citekey))
            for c in citekeys:
                p = repo.pull_paper(c)
                ui.message('    {}'.format(pretty.paper_oneliner(p)))
            if exit_on_fail:
                ui.exit()
    return citekey


def resolve_citekey_list(repo, citekeys, ui=None, exit_on_fail=True):
    shutdown = False
    keys = []
    for key in citekeys:
        try:
            keys.append(resolve_citekey(repo, key, ui, exit_on_fail))
        except SystemExit:
            shutdown = exit_on_fail

    if shutdown and ui is not None:
        ui.exit()
    else:
        return keys


def standardize_doi(doi):
    """
    Given a putative doi, attempts to always return it in the form of
    10.XXXX/...  Specifically designed to handle these cases:
    -   https://doi.org/<doi>
    -   http://doi.org/<doi>
    -   https://dx.doi.org/<doi>
    -   http://dx.doi.org/<doi>
    -   dx.doi.org/<doi>
    -   doi.org/<doi>
    and attempts to verify doi adherence to DOI handbook standards and
    crossref.org advice:
    https://www.doi.org/doi_handbook/2_Numbering.html
    https://www.crossref.org/blog/dois-and-matching-regular-expressions/

        :returns standardized doi
    """

    doi_regexes = (
        '(10\.\d{4,9}/[-._;()/:A-z0-9\>\<]+)',
        '(10.1002/[^\s]+)',
        '(10\.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d)',
        '(10\.1021/\w\w\d+\+)',
        '(10\.1207/[\w\d]+\&\d+_\d+)')
    doi_pattern = re.compile('|'.join(doi_regexes))

    match = doi_pattern.search(doi)
    if not match:
        raise ValueError("Not a valid doi: {}".format(doi))
    new_doi = match.group(0)

    return new_doi
