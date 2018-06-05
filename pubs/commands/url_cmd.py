from __future__ import unicode_literals

import webbrowser

from .. import repo
from ..uis import get_ui
from ..utils import resolve_citekey_list



def parser(subparsers, conf):
    parser = subparsers.add_parser('url',
                                   help="open a paper's url in the default web browser")
    parser.add_argument("citekey", nargs = '*',
                        help="one or more citeKeys to open")
    return parser


def command(conf, args):
    """Open the url of one or several papers in a web browser."""

    ui = get_ui()
    rp = repo.Repository(conf)

    for key in resolve_citekey_list(rp, args.citekey, ui=ui, exit_on_fail=False):
        try:
            paper = rp.pull_paper(key)
            url = paper.bibdata['url']
            ui.info('opening url {}'.format(url))
            webbrowser.open(url)

        except KeyError as e:
            ui.warning('{} has no url'.format(key))

    rp.close()
