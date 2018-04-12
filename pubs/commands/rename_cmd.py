from __future__ import unicode_literals

from ..uis import get_ui
from .. import color
from .. import repo
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion


def parser(subparsers, conf):
    parser = subparsers.add_parser('rename',
                                   help='rename the citekey of a repository')
    parser.add_argument('citekey', help='current citekey'
                        ).completer = CiteKeyCompletion(conf)
    parser.add_argument('new_citekey', help='new citekey')
    return parser


def command(conf, args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = get_ui()
    rp = repo.Repository(conf)

    # TODO: here should be a test whether the new citekey is valid
    key = resolve_citekey(repo=rp, citekey=args.citekey, ui=ui, exit_on_fail=True)
    paper = rp.pull_paper(key)
    rp.rename_paper(paper, args.new_citekey)
    ui.message("The '{}' citekey has been renamed into '{}'".format(
        color.dye_out(args.citekey, 'citekey'),
        color.dye_out(args.new_citekey, 'citekey')))

    rp.close()
