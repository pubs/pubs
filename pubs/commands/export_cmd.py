from __future__ import unicode_literals

import argparse

from .. import repo
from ..uis import get_ui
from .. import endecoder
from ..utils import resolve_citekey_list
from ..endecoder import BIBFIELD_ORDER
from ..completion import CiteKeyCompletion, CommaSeparatedListCompletion


class CommaSeparatedList(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [s for s in values.split(',') if s])


class FieldCommaSeparatedListCompletion(CommaSeparatedListCompletion):

    values = BIBFIELD_ORDER


def parser(subparsers, conf):
    parser = subparsers.add_parser('export', help='export bibliography')
    parser.add_argument(
        '--ignore-fields', default=[], action=CommaSeparatedList,
        help='exclude field(s) from output (comma separated if multiple)'
    ).completer = FieldCommaSeparatedListCompletion(conf)
    # parser.add_argument('-f', '--bib-format', default='bibtex',
    #         help='export format')
    parser.add_argument('citekeys', nargs='*', help='one or several citekeys'
                        ).completer = CiteKeyCompletion(conf)
    return parser


def command(conf, args):
    """
    """
    # :param bib_format (only 'bibtex' now)

    ui = get_ui()
    rp = repo.Repository(conf)

    papers = []
    if len(args.citekeys) < 1:
        papers = rp.all_papers()
    else:
        for key in resolve_citekey_list(repo=rp, citekeys=args.citekeys, ui=ui, exit_on_fail=True):
            papers.append(rp.pull_paper(key))

    bib = {}
    for p in papers:
        bib[p.citekey] = p.bibdata

    exporter = endecoder.EnDecoder()
    bibdata_raw = exporter.encode_bibdata(bib, args.ignore_fields)
    ui.message(bibdata_raw)

    rp.close()
