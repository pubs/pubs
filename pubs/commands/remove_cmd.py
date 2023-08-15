from __future__ import unicode_literals

from .. import repo
from .. import color
from .. import pretty
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

    keys = resolve_citekey_list(rp, conf, args.citekeys, ui=ui, exit_on_fail=True)
    plural = 's' if len(keys) > 1 else ''

    if force is None:
        to_remove_str = '\n'.join(pretty.paper_oneliner(rp.pull_paper(key),
                                                        max_authors=conf['main']['max_authors'])
                                  for key in keys)
        are_you_sure = (("Are you sure you want to delete the following publication{}"
            " (this will also delete associated documents)?:\n{}\n")
            .format(plural, to_remove_str))
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

            ui.message('The publication{} {} were removed'.format(plural,
                ', '.join([color.dye_out(c, 'citekey') for c in keys])))

        # FIXME: print should check that removal proceeded well.
    else:
        ui.message('The publication{} {} were {} removed'.format(plural,
            ', '.join([color.dye_out(c, 'citekey') for c in keys]),
            color.dye_out('not','bold')))
