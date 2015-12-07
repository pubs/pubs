from .. import repo
from .. import color
from ..uis import get_ui


def parser(subparsers):
    parser = subparsers.add_parser('remove', help='removes a paper')
    parser.add_argument('-f', '--force', action='store_true', default=None,
                        help="does not prompt for confirmation.")
    parser.add_argument('citekeys', nargs='*',
                        help="one or several citekeys")
    return parser


def command(conf, args):

    ui = get_ui()
    force = args.force
    rp = repo.Repository(conf)

    if force is None:
        are_you_sure = (("Are you sure you want to delete paper(s) [{}]"
            " (this will also delete associated documents)?")
            .format(', '.join([color.dye_out(c, 'citekey') for c in args.citekeys])))
        sure = ui.input_yn(question=are_you_sure, default='n')
    if force or sure:
        for c in args.citekeys:
            rp.remove_paper(c)
            ui.message('The paper(s) [{}] were removed'.format(', '.join([color.dye_out(c, 'citekey') for c in args.citekeys])))
            # FIXME: print should check that removal proceeded well.
    else:
        ui.message('The paper(s) [{}] were *not* removed'.format(', '.join([color.dye_out(c, 'citekey') for c in args.citekeys])))
