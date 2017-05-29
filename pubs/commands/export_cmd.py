from __future__ import print_function

from .. import repo
from ..uis import get_ui
from .. import endecoder
from ..utils import resolve_citekey_list

def parser(subparsers):
    parser = subparsers.add_parser('export', help='export bibliography')
    # parser.add_argument('-f', '--bib-format', default='bibtex',
    #         help='export format')
    parser.add_argument('citekeys', nargs='*', help='one or several citekeys')
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
    bibdata_raw = exporter.encode_bibdata(bib, conf['main']['keylist'])
    ui.message(bibdata_raw)

    rp.close()
