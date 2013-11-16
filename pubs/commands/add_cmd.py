import datetime

from ..uis import get_ui
from ..configs import config
from .. import bibstruct
from .. import content
from .. import repo
from .. import paper
from .. import templates


def parser(subparsers):
    parser = subparsers.add_parser('add', help='add a paper to the repository')
    parser.add_argument('-b', '--bibfile',
                        help='bibtex, bibtexml or bibyaml file', default=None)
    parser.add_argument('-d', '--docfile', help='pdf or ps file', default=None)
    parser.add_argument('-t', '--tags', help='tags associated to the paper, separated by commas',
                        default=None)
    parser.add_argument('-k', '--citekey', help='citekey associated with the paper;\nif not provided, one will be generated automatically.',
                        default=None)
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    return parser


def bibdata_from_editor(rp):
    again = True
    try:
        bibstr = content.editor_input(config().edit_cmd,
                                      templates.add_bib,
                                      suffix='.bib')
        if bibstr == templates.add_bib:
            cont = ui.input_yn(
                question='Bibfile not edited. Edit again ?',
                default='y')
            if not cont:
                ui.exit(0)
        else:
            bibdata = rp.databroker.verify(bibstr)
            bibstruct.verify_bibdata(bibdata)
            # REFACTOR Generate citykey
            cont = False
    except ValueError:
        again = ui.input_yn(
            question='Invalid bibfile. Edit again ?',
            default='y')
        if not again:
            ui.exit(0)

    return bibdata

def command(args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = get_ui()
    bibfile = args.bibfile
    docfile = args.docfile
    tags = args.tags
    citekey = args.copy

    rp = repo.Repository(config())

    # get bibfile

    if bibfile is None:
        bibdata = bibdata_from_editor(rp)
    else:
        bibdata_raw = content.get_content(bibfile)
        bibdata = rp.databroker.verify(bibdata_raw)
        if bibdata is None:
            ui.error('invalid bibfile {}.'.format(bibfile))

    # citekey

    citekey = args.citekey
    if citekey is None:
        base_key = bibstruct.extract_citekey(bibdata)
        citekey = rp.unique_citekey(base_key)
    else:
        rp.databroker.exists(citekey, both=False)

    # tags

    if tags is not None:
        p.tags = set(tags.split(','))

    p = paper.Paper(bibdata, citekey=citekey)
    p.added = datetime.datetime.now()

    # document file

    bib_docfile = bibstruct.extract_docfile(bibdata)
    if docfile is None:
        docfile = bib_docfile
    elif bib_docfile is not None:
        ui.warning(('Skipping document file from bib file '
                    '{}, using {} instead.').format(bib_docfile, docfile))

    if docfile is not None:
        copy_doc = args.copy
        if copy_doc is None:
            copy_doc = config().import_copy
        if copy_doc:
            docfile = rp.databroker.copy_doc(citekey, docfile)

    # create the paper

    try:
        p.docpath = docfile
        rp.push_paper(p)
    except ValueError, v:
        ui.error(v.message)
        ui.exit(1)
