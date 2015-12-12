from ..uis import get_ui
from .. import bibstruct
from .. import content
from .. import repo
from .. import paper

def parser(subparsers):
    parser = subparsers.add_parser('rename', help='rename the citekey of a repository')
    parser.add_argument('citekey',
                        help='current citekey')
    parser.add_argument('new_citekey',
                        help='new citekey')
    return parser


def command(conf, args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = get_ui()
    rp = repo.Repository(conf)

    paper = rp.pull_paper(args.citekey)
    rp.rename_paper(paper, args.new_citekey)
