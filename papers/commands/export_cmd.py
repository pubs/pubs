from __future__ import print_function
import sys

from pybtex.database import BibliographyData

from .. import repo
from ..configs import config
from ..uis import get_ui
from .. import endecoder

def parser(subparsers):
    parser = subparsers.add_parser('export',
            help='export bibliography')
    parser.add_argument('-f', '--bib-format', default='bibtex',
            help='export format')
    parser.add_argument('citekeys', nargs='*',
            help='one or several citekeys')
    return parser


def command(args):
    """
    :param bib_format       (in 'bibtex', 'yaml')
    """

    ui = get_ui()
    bib_format = args.bib_format

    rp = repo.Repository(config())

    try:
        papers = [rp.pull_paper(c) for c in args.citekeys]
    except repo.InvalidReference, v:
        ui.error(v)
        ui.exit(1)

    if len(papers) == 0:
        papers = rp.all_papers()
    bib = BibliographyData()
    for p in papers:
        bib.add_entry(p.citekey, p.bibentry)
    try:
        exporter = endecoder.EnDecoder()
        bibdata_raw = exporter.encode_bibdata(bib, fmt=bib_format)
        print(bibdata_raw, end='')
    except KeyError:
        ui.error("Invalid output format: %s." % bib_format)
