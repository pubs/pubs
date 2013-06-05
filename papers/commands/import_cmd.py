from .. import repo
from ..paper import Paper, NoDocumentFile
from .. import files


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
        copy = config.get('papers', 'import-copy')
    rp = repo.Repository.from_directory()
    # Extract papers from bib
    papers = Paper.many_from_path(bibpath, fatal=False)
    for p in papers:
        doc_file = None
        try:
            file_path = p.get_document_file_from_bibdata(remove=True)
            if files.check_file(file_path):
                doc_file = file_path
            else:
                print("File does not exist for %s (%s)."
                      % (p.citekey, file_path))
        except NoDocumentFile:
            print "No file for %s." % p.citekey
        rp.add_paper(p)
        if doc_file:
            if copy:
                rp.import_document(p.citekey, doc_file)
            else:
                p.set_external_document(doc_file)
                rp.add_or_update(p)
