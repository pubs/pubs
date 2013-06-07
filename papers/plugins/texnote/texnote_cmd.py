#from ... import pretty
#from ... import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('texnote', help="edit advance note in latex")
    return parser


def command(config, ui):
    ui.print_('texnote test')
