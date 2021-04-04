from __future__ import unicode_literals

from ..paper import Paper
from .. import repo
from .. import color

from ..uis import get_ui
from ..endecoder import EnDecoder
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion
from ..events import ModifyEvent

from .show_cmd import show
from .. import pretty
from .. import bibstruct

def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'search',
        help='search papers in the repository from an author or with given keywords in the title')
    parser.add_argument(
        '-a', '--author', default=False,
        help='search with the author name')
    parser.add_argument(
        '-t', '--title', default=False,
        help='search with the keywords in the title')
    return parser


def command(conf, args):
    ui = get_ui()
    rp = repo.Repository(conf)
    target_author = args.author
    keywords = args.title
    papers = list(rp.all_papers())
    
    if target_author:
        if keywords:
            for paper in papers:
                if paper.bibdata and 'author' in paper.bibdata and paper.bibdata['author'] and 'title' in paper.bibdata and paper.bibdata['title']:
                    for author in paper.bibdata['author']:
                        if target_author in author and keywords in paper.bibdata['title']:
                            show(ui, conf, paper)
                            print()
        else:
            for paper in papers:
                if paper.bibdata and 'author' in paper.bibdata and paper.bibdata['author']:
                    for author in paper.bibdata['author']:
                        if target_author in author:
                            show(ui, conf, paper)
                            print()
    else:                    
        if keywords:
            for paper in papers:
                if paper.bibdata and 'title' in paper.bibdata and paper.bibdata['title'] and keywords in paper.bibdata['title']:
                    show(ui, conf, paper)
                    print()
