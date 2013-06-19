from .. import files
from .. import color
from ..repo import InvalidReference


def add_references_argument(parser, single=False):
    if single:
        parser.add_argument('reference',
                help='reference to the paper (citekey or number)')
    else:
        parser.add_argument('references', nargs='*',
                help="one or several reference to export (citekeysor numbers)")


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


def parse_reference(ui, rp, ref):
    try:
        return rp.citekey_from_ref(ref)
    except InvalidReference:
        ui.error("no paper with reference: %s."
                    % color.dye(ref, color.citekey))
        ui.exit(-1)


def parse_references(ui, rp, refs):
    citekeys = [parse_reference(ui, rp, ref) for ref in refs]
    return citekeys
