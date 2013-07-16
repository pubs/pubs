from .. import repo
from ..paper import Paper
from .helpers import add_paper_with_docfile, extract_doc_path_from_bibdata
from ..configs import config
from ..uis import get_ui


def parser(subparsers):
    parser = subparsers.add_parser('import',
            help='import paper(s) to the repository')
    parser.add_argument('bibpath',
            help='path to bibtex, bibtexml or bibyaml file (or directory)')
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    parser.add_argument('keys', nargs='*',
            help="one or several keys to import from the file")
    return parser


def command(args):
    """
    :param bibpath: path (no url yet) to a bibliography file
    """

    ui = get_ui()
    bibpath = args.bibpath
    copy = args.copy

    if copy is None:
        copy = config().import_copy
    rp = repo.Repository(config())
    # Extract papers from bib
    papers = Paper.many_from_path(bibpath)
    keys = args.keys or papers.keys()
    for k in keys:
        try:
            p = papers[k]
            if isinstance(p, Exception):
                ui.error('Could not load entry for citekey {}.'.format(k))
            else:
                doc_file = extract_doc_path_from_bibdata(p)
                if doc_file is None:
                    ui.warning("No file for %s." % p.citekey)
                add_paper_with_docfile(rp, p, docfile=doc_file, copy=copy)
        except KeyError:
            ui.error('No entry found for citekey {}.'.format(k))
