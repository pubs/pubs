from ..repo import Repository


def parser(subparsers, config):
    parser = subparsers.add_parser('tags', help="list existing tags")
    return parser


def command(config, ui):
    """List existing tags"""
    rp = Repository.from_directory(config)
    for tag in rp.get_labels():
        ui.print_(tag)
