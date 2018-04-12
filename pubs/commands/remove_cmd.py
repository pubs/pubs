from __future__ import unicode_literals

from .. import repo
from .. import color
from ..uis import get_ui
from ..utils import resolve_citekey_list
from ..p3 import ustr, u_maybe
from ..completion import CiteKeyCompletion


def parser(subparsers, conf):
    parser = subparsers.add_parser('remove', help='removes a publication')
    parser.add_argument('-f', '--force', action='store_true', default=None,
                        help="does not prompt for confirmation.")
    parser.add_argument('citekeys', nargs='+', type=u_maybe,
                        help="one or several citekeys",
                        ).completer = CiteKeyCompletion(conf)
    return parser


def command(conf, args):

    ui = get_ui()
    force = args.force
    rp = repo.Repository(conf)

    keys = resolve_citekey_list(repo=rp, citekeys=args.citekeys, ui=ui, exit_on_fail=True)

    if force is None:
        are_you_sure = (("Are you sure you want to delete the publication(s) [{}]"
            " (this will also delete associated documents)?")
            .format(', '.join([color.dye_out(c, 'citekey') for c in args.citekeys])))
        sure = ui.input_yn(question=are_you_sure, default='n')
    if force or sure:
        failed = False  # Whether something failed
        for c in keys:
            try:
                rp.remove_paper(c)
            except Exception as e:
                ui.error(ustr(e))
                failed = True
        if failed:
            ui.exit()  # Exit with nonzero error code
        else:
            ui.message('The publication(s) [{}] were removed'.format(
                ', '.join([color.dye_out(c, 'citekey') for c in keys])))

        # FIXME: print should check that removal proceeded well.
    else:
        ui.message('The publication(s) [{}] were {} removed'.format(
            ', '.join([color.dye_out(c, 'citekey') for c in keys]),
            color.dye_out('not','bold')))
