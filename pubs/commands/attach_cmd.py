from .. import repo
from .. import color
from ..configs import config
from ..uis import get_ui
from .. import content

def parser(subparsers):
    parser = subparsers.add_parser('attach',
            help='attach a document to an existing paper')
    # parser.add_argument('-c', '--copy', action='store_true', default=True,
    #         help="copy document files into library directory (default)")
    parser.add_argument('-L', '--link', action='store_false', dest='copy', default=True,
            help="don't copy document files, just create a link.")
    parser.add_argument('-M', '--move', action='store_true', dest='move', default=False,
            help="move document instead of of copying (ignored if --link).")
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

    try:
        document = args.document
        rp.push_doc(paper.citekey, document, copy=args.copy)
        if args.copy:
            if args.move:
                content.remove_file(document)
            # else:
            #     if ui.input_yn('{} has been copied into pubs; should the original be removed?'.format(color.dye_out(document, 'bold'))):
            #         content.remove_file(document)

        ui.message('{} attached to {}'.format(color.dye_out(document, 'bold'), color.dye_out(paper.citekey, color.citekey)))

    except ValueError as v:
        ui.error(v.message)
        ui.exit(1)
    except IOError as v:
        ui.error(v.message)
        ui.exit(1)
