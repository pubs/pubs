from .. import repo
from .. import color
from .helpers import add_references_argument, parse_references


def parser(subparsers, config):
    parser = subparsers.add_parser('remove', help='removes a paper')
    add_references_argument(parser)
    return parser


def command(config, ui, references):
    rp = repo.Repository.from_directory(config)
    citekeys = parse_references(ui, rp, references)
    are_you_sure = ("Are you sure you want to delete paper(s) [%s]"
        " (this will also delete associated documents)?"
        % ', '.join([color.dye(c, color.citekey) for c in citekeys]))
    sure = ui.input_yn(question=are_you_sure, default='n')
    if sure:
        for c in citekeys:
            rp.remove(c)
