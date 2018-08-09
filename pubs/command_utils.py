"""Contains code that is reused over commands, like argument definition
or help messages.
"""


def add_doc_add_arguments(parser, move=True):
    doc_add_group = parser.add_mutually_exclusive_group()
    doc_add_group.add_argument(
        '-L', '--link', action='store_const', dest='doc_add', const='link',
        default=None,
        help="don't copy document files, just create a link.")
    doc_add_group.add_argument(
        '-C', '--copy', action='store_const', dest='doc_add', const='copy',
        default=None,
        help="copy document (keep source).")
    if move:
        doc_add_group.add_argument(
            '-M', '--move', action='store_const', dest='doc_add', const='move',
            default=None,
            help="move document (copy and remove source).")
