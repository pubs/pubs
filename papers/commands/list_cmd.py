import subprocess
import tempfile

from .. import pretty
from .. import color
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser


def command(config):
    rp = repo.Repository.from_directory()
    articles = []
    for n in range(rp.size()):
        paper = rp.paper_from_number(n, fatal=True)
        bibdesc = pretty.bib_oneliner(paper.bibentry)
        articles.append((u'{:3d} {}{}{}{}   {}'.format(int(n), color.purple, rp.citekeys[n], color.end, (10 - len(paper.citekey))*' ', bibdesc)).encode('utf-8'))

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=True) as tmpf:
        tmpf.write('\n'.join(articles))
        tmpf.flush()
        subprocess.call(['less', '-XRF', tmpf.name])
