from __future__ import unicode_literals

import webbrowser

from .. import p3
from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey, resolve_citekey_list



def parser(subparsers, conf):
    parser = subparsers.add_parser('url',
                                   help="open the url in the browser")
    parser.add_argument("citekey", nargs = '*',
                        help="one or more citeKeys to open")
    return parser


def command(conf, args):
    """Open the url for a publication."""

    ui = get_ui()
    rp = repo.Repository(conf)

    for key in resolve_citekey_list(rp, args.citekey, ui=ui, exit_on_fail=True):
        try:
            paper = rp.pull_paper(key)
            url = paper.bibdata['url']
            webbrowser.open(url)

        except KeyError as e:
            ui.error('{} has no url'.format(key))

    rp.close()
