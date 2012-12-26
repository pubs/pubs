import os
import sys
import shutil

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


def command(config, bibpath, copy):
    """
    :param pdffilepath  path (no url yet) to a pdf or ps file
    :param bibtex       bibtex file (in .bib, .bibml or .yaml format.
    """
    if copy is None:
        copy = config.get('papers', 'import-copy')
    rp = repo.Repository.from_directory()
    # Get directory for document
    doc_path = files.clean_path(rp.get_document_directory(config))
    if not (os.path.exists(doc_path) and os.path.isdir(doc_path)):
        print "Document directory %s, does not exist." % doc_path
        sys.exit(1)
    # Extract papers from bib
    papers = Paper.many_from_path(bibpath, fatal=False)
    for p in papers:
        doc_file = None
        try:
            file_path = p.get_document_file_from_bibdata(remove=True)
            if os.path.exists(file_path):
                doc_file = file_path
            else:
                print "File does not exist for %s." % p.citekey
        except NoDocumentFile:
            print "No file for %s." % p.citekey
        rp.add_paper(p)
        if doc_file:
            if copy:
                ext = os.path.splitext(doc_file)[1]
                new_doc_file = os.path.join(doc_path, p.citekey + ext)
                shutil.copy(doc_file, new_doc_file)
            else:
                new_doc_file = doc_file
            p.set_document(new_doc_file)
            rp.add_or_update(p)
