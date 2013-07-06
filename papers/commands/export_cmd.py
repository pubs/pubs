import sys

from pybtex.database import BibliographyData

from .. import repo
from .. import files
from .helpers import parse_references, add_references_argument
from ..configs import config
from ..uis import get_ui

def parser(subparsers):
    parser = subparsers.add_parser('export',
            help='export bibliography')
    parser.add_argument('-f', '--bib-format', default='bibtex',
            help="export format")
    add_references_argument(parser)
    return parser


def command(args):
    """
    :param bib_format       (in 'bibtex', 'yaml')
    """

    ui = get_ui()
    bib_format = args.bib_format
    references = args.references

    rp = repo.Repository(config())
    papers = [rp.get_paper(c)
              for c in parse_references(rp, references)]
    if len(papers) == 0:
        papers = rp.all_papers()
    bib = BibliographyData()
    for p in papers:
        bib.add_entry(p.citekey, p.bibentry)
    try:
        files.write_bibdata(bib, sys.stdout, bib_format)
    except KeyError:
        ui.error("Invalid output format: %s." % bib_format)
