from .. import repo
from .. import color
from ..configs import config
from .helpers import add_references_argument, parse_references

from ..events import RemoveEvent


def parser(subparsers):
    parser = subparsers.add_parser('remove', help='removes a paper')
    parser.add_argument('-f', '--force', action='store_true', default=None,
    help="does not prompt for confirmation.")
    add_references_argument(parser)
    return parser


def command(args):

    ui = args.ui
    force = args.force
    references = args.references

    rp = repo.Repository(config())
    citekeys = parse_references(ui, rp, references)
    if force is None:
        are_you_sure = ("Are you sure you want to delete paper(s) [%s]"
            " (this will also delete associated documents)?"
            % ', '.join([color.dye(c, color.citekey) for c in citekeys]))
        sure = ui.input_yn(question=are_you_sure, default='n')
    if force or sure:
        for c in citekeys:
            rmevent = RemoveEvent(ui, c)
            rmevent.send()

            rp.remove_paper(c)
