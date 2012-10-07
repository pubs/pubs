import webbrowser
import urllib

def parser(subparsers, config):
    parser = subparsers.add_parser('websearch', help="launch a search on Google Scholar")
    parser.add_argument("search_string", help="the search query (anything googly is possible)")
    return parser

def command(config, search_string):
    url = 'https://scholar.google.fr/scholar?q={}&lr='.format(urllib.quote_plus(search_string))
    webbrowser.open(url)