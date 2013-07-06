from .. import files
from .. import color
from .. import pretty
from ..repo import InvalidReference
from ..paper import NoDocumentFile
from ..uis import get_ui


def add_references_argument(parser, single=False):
    if single:
        parser.add_argument('reference',
                help='reference to the paper (citekey or number)')
    else:
        parser.add_argument('references', nargs='*',
                help="one or several reference to export (citekeysor numbers)")


def add_docfile_to_paper(repo, paper, docfile, copy=False):
    if copy:
        repo.import_document(paper.citekey, docfile)
    else:
        paper.set_external_document(docfile)
        repo.add_or_update(paper)


def add_paper_with_docfile(repo, paper, docfile=None, copy=False):
    repo.add_paper(paper)
    if docfile is not None:
        add_docfile_to_paper(repo, paper, docfile, copy=copy)


def extract_doc_path_from_bibdata(paper):
    try:
        file_path = paper.get_document_file_from_bibdata(remove=True)
        if files.check_file(file_path):
            return file_path
        else:
            ui = get_ui()
            ui.warning("File does not exist for %s (%s)."
                       % (paper.citekey, file_path))
    except NoDocumentFile:
        return None


def parse_reference(rp, ref):
    try:
        return rp.ref2citekey(ref)
    except InvalidReference:
        ui = get_ui()
        ui.error("no paper with reference: %s."
                    % color.dye(ref, color.citekey))
        ui.exit(-1)


def parse_references(rp, refs):
    citekeys = [parse_reference(rp, ref) for ref in refs]
    return citekeys

def paper_oneliner(p, n = 0, citekey_only = False):
    if citekey_only:
        return p.citekey
    else:
        bibdesc = pretty.bib_oneliner(p.bibentry)
        return (u'{num:d}: [{citekey}] {descr} {tags}'.format(
            num=int(n),
            citekey=color.dye(p.citekey, color.purple),
            descr=bibdesc,
            tags=color.dye(' '.join(p.tags),
                           color.purple, bold=True),
            )).encode('utf-8')
