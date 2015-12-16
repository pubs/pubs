from ..uis import get_ui
from .. import repo
from ..utils import resolve_citekey

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

    # TODO: here should be a test whether the new citekey is valid
    try:
        key = resolve_citekey(repo=rp, citekey=args.citekey, ui=ui, exit_on_fail=True)
        paper = rp.pull_paper(key)
        rp.rename_paper(paper, args.new_citekey)
    except Exception as e:
        ui.error(e.message)