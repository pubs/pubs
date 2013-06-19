from .. import repo
from ..paper import Paper
from .helpers import add_paper_with_docfile, extract_doc_path_from_bibdata
from .. import configs


def parser(subparsers, config):
    parser = subparsers.add_parser('import',
            help='import paper(s) to the repository')
    parser.add_argument('bibpath',
            help='path to bibtex, bibtexml or bibyaml file (or directory)')
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    return parser


def command(config, ui, bibpath, copy):
    """
    :param bibpath: path (no url yet) to a bibliography file
    """
    if copy is None:
        copy = config.get(configs.MAIN_SECTION, 'import-copy')
    rp = repo.Repository.from_directory(config)
    # Extract papers from bib
    papers = Paper.many_from_path(bibpath, fatal=False)
    for p in papers:
        doc_file = extract_doc_path_from_bibdata(p, ui)
        if doc_file is None:
            ui.warning("No file for %s." % p.citekey)
        add_paper_with_docfile(rp, p, docfile=doc_file, copy=copy)
