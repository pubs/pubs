from __future__ import unicode_literals

import os
from .. import p3
from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import NoteEvent
from ..content import write_file
from ..content import read_text_file


def parser(subparsers, conf):
    parser = subparsers.add_parser('note',
                                   help='edit the note attached to a paper')
    parser.add_argument('citekey', help='citekey of the paper',
                        ).completer = CiteKeyCompletion(conf)
    parser.add_argument('-a', '--append',
                        help='append a line of text to the notes file', default=None)
    parser.add_argument('-e', '--echo', action='store_true',
                        help='echo the contents of the notes file')
    return parser


def command(conf, args):

    ui = get_ui()
    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    notepath = rp.databroker.real_notepath(citekey, rp.conf['main']['note_extension'])
    # Edit bib file in an editor
    if args.append is None and not args.echo:
        ui.edit_file(notepath, temporary=False)
    # or Append bib file from the command line
    elif args.append:
        latestnote = '{txt}\n'.format(txt=p3.u_maybe(args.append))
        write_file(notepath, latestnote, 'a')
    # then Echo the contents of the bib file, if requested
    if args.echo and os.path.exists(notepath):
        print(read_text_file(notepath, fail=False))
    NoteEvent(citekey).send()
    rp.close()
