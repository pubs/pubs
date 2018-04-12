from __future__ import unicode_literals

import webbrowser

from .. import p3
from ..uis import get_ui


def parser(subparsers, conf):
    parser = subparsers.add_parser('websearch',
                                   help="launch a search on Google Scholar")
    parser.add_argument("search_string", nargs = '*',
                        help="the search query (anything googly is possible)")
    return parser


def command(conf, args):

    ui = get_ui()
    search_string = args.search_string

    url = ("https://scholar.google.fr/scholar?q=%s&lr="
           % (p3.quote_plus(' '.join(search_string))))
    webbrowser.open(url)
