"""Contains code that is reused over commands, like argument definition
or help messages.
"""


def add_doc_copy_arguments(parser, copy=True):
    doc_add_group = parser.add_mutually_exclusive_group()
    doc_add_group.add_argument(
        '-L', '--link', action='store_const', dest='doc_copy', const='link',
        default=None,
        help="don't copy document files, just create a link.")
    if copy:
        doc_add_group.add_argument(
            '-C', '--copy', action='store_const', dest='doc_copy', const='copy',
            help="copy document (keep source).")
    doc_add_group.add_argument(
        '-M', '--move', action='store_const', dest='doc_copy', const='move',
        help="move document (copy and remove source).")
