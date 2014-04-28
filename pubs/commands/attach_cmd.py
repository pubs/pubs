from .. import repo
from ..configs import config
from ..uis import get_ui

def parser(subparsers):
    parser = subparsers.add_parser('attach',
            help='attach a document to an existing paper')
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    parser.add_argument('citekey',
            help='citekey of the paper')
    parser.add_argument('document',
            help='document file')
    return parser


def command(args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = get_ui()

    rp = repo.Repository(config())
    paper = rp.pull_paper(args.citekey)

    try:
        document = args.document
        document = rp.push_doc(paper.citekey, document, copy=args.copy)
    except ValueError as v:
        ui.error(v.message)
        ui.exit(1)
    except IOError as v:
        ui.error(v.message)
        ui.exit(1)
