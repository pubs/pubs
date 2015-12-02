from __future__ import print_function

from .. import repo
from ..configs import config
from ..uis import get_ui
from .. import endecoder


def parser(subparsers):
    parser = subparsers.add_parser('export', help='export bibliography')
    # parser.add_argument('-f', '--bib-format', default='bibtex',
    #         help='export format')
    parser.add_argument('citekeys', nargs='*', help='one or several citekeys')
    return parser


def command(args):
    """
    """
    # :param bib_format (only 'bibtex' now)

    ui = get_ui()

    rp = repo.Repository(config())

    try:
        papers = [rp.pull_paper(c) for c in args.citekeys]
    except repo.InvalidReference as v:
        ui.error(v)
        ui.exit(1)

    if len(papers) == 0:
        papers = rp.all_papers()
    bib = {}
    for p in papers:
        bib[p.citekey] = p.bibdata
    exporter = endecoder.EnDecoder()
    bibdata_raw = exporter.encode_bibdata(bib)
    ui.print_out(bibdata_raw)
