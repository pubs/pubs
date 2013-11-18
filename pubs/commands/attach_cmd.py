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

    copy = args.copy
    if copy is None:
        copy = config().import_copy

    try:
        document = args.document
        if copy:
            document = rp.databroker.copy_doc(paper.citekey, document)
        else:
            pass # TODO warn if file does not exists
        paper.docpath = document
        rp.push_paper(paper, overwrite=True, event=False)
    except ValueError, v:
        ui.error(v.message)
        ui.exit(1)
    except IOError, v:
        ui.error(v.message)
        ui.exit(1)
