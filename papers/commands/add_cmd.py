from .. import repo
from .. import files
from ..paper import Paper, NoDocumentFile, get_bibentry_from_string
from ..configs import config
from .helpers import add_paper_with_docfile, extract_doc_path_from_bibdata


def parser(subparsers):
    parser = subparsers.add_parser('add', help='add a paper to the repository')
    parser.add_argument('-b', '--bibfile',
                        help='bibtex, bibtexml or bibyaml file', default=None)
    parser.add_argument('-d', '--docfile', help='pdf or ps file', default=None)
    parser.add_argument('-t', '--tags', help='tags associated to the paper, separated by commas',
                        default=None)
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    return parser


def command(args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = args.ui
    bibfile = args.bibfile
    docfile = args.docfile
    tags = args.tags
    copy = args.copy

    if copy is None:
        copy = config().import_copy
    rp = repo.Repository(config())
    if bibfile is None:
        cont = True
        bibstr = ''
        while cont:
            try:
                bibstr = files.editor_input(config, bibstr, suffix='.yaml')
                key, bib = get_bibentry_from_string(bibstr)
                cont = False
            except Exception:
                cont = ui.input_yn(
                    question='Invalid bibfile. Edit again ?',
                    default='y')
                if not cont:
                    ui.exit()
        p = Paper(bibentry=bib, citekey=key)
    else:
        p = Paper.load(bibfile)
    if tags is not None:
        p.tags = set(tags.split(','))
    # Check if another doc file is specified in bibtex
    docfile2 = extract_doc_path_from_bibdata(p, ui)
    if docfile is None:
        docfile = docfile2
    elif docfile2 is not None:
        ui.warning(
                "Skipping document file from bib file: %s, using %s instead."
                % (docfile2, docfile))
    try:
        add_paper_with_docfile(rp, p, docfile=docfile, copy=copy)
    except ValueError, v:
        ui.error(v.message)
        ui.exit(1)
# TODO handle case where citekey exists
