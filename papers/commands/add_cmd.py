from .. import repo
from .. import files
from ..paper import Paper, NoDocumentFile


def add_paper_with_docfile(repo, paper, docfile=None, copy=False):
    repo.add_paper(paper)
    if docfile is not None:
        if copy:
            repo.import_document(paper.citekey, docfile)
        else:
            paper.set_external_document(docfile)
            repo.add_or_update(paper)


def extract_doc_path_from_bibdata(paper, ui):
    try:
        file_path = paper.get_document_file_from_bibdata(remove=True)
        if files.check_file(file_path):
            return file_path
        else:
            ui.warning("File does not exist for %s (%s)."
                        % (paper.citekey, file_path))
    except NoDocumentFile:
        return None


def parser(subparsers, config):
    parser = subparsers.add_parser('add', help='add a paper to the repository')
    parser.add_argument('bibfile', help='bibtex, bibtexml or bibyaml file')
    parser.add_argument('-d', '--docfile', help='pdf or ps file', default=None)
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    return parser


def command(config, ui, bibfile, docfile, copy):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """
    if copy is None:
        copy = config.get('papers', 'import-copy')
    rp = repo.Repository.from_directory()
    p = Paper.load(bibfile)
    # Check if another doc file is specified in bibtex
    docfile2 = extract_doc_path_from_bibdata(p, ui)
    if docfile is None:
        docfile = docfile2
    elif docfile2 is not None:
        ui.warning(
                "Skipping document file from bib file: %s, using %s instead."
                % (docfile2, docfile))
    add_paper_with_docfile(rp, p, docfile=docfile, copy=copy)
