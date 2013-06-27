import webbrowser
import urllib


def parser(subparsers, config):
    parser = subparsers.add_parser('websearch',
                                   help="launch a search on Google Scholar")
    parser.add_argument("search_string", nargs = '*',
                        help="the search query (anything googly is possible)")
    return parser


def command(config, ui, search_string):
    print search_string
    url = ("https://scholar.google.fr/scholar?q=%s&lr="
           % (urllib.quote_plus(' '.join(search_string))))
    webbrowser.open(url)
