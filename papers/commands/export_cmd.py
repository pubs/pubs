import sys

from pybtex.database import BibliographyData

from .. import repo
from .. import files


def parser(subparsers, config):
    parser = subparsers.add_parser('export',
            help='export bibliography')
    parser.add_argument('-f', '--bib-format', default='bibtex',
            help="export format")
    return parser


def command(config, ui, bib_format):
    """
    :param bib_format       (in 'bibtex', 'yaml')
    """
    rp = repo.Repository.from_directory(config)
    bib = BibliographyData()
    for p in rp.all_papers():
        bib.add_entry(p.citekey, p.bibentry)
    try:
        files.write_bibdata(bib, sys.stdout, bib_format)
    except KeyError:
        ui.error("Invalid output format: %s." % bib_format)
