import subprocess
import tempfile

from .. import pretty
from .. import color
from .. import repo

def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser

def command(config):
    rp = repo.Repository()
    
    articles = []
    for n in sorted(rp.numbers.keys()):
        paper = rp.paper_from_number(n, fatal = True)
        bibdesc = pretty.bib_oneliner(paper.bib_data)
        articles.append(u'{:3d} {}{}{}{}   {}'.format(int(paper.number), color.purple, paper.citekey, color.end, (8-len(paper.citekey))*' ', bibdesc))

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=True) as tmpf:
        tmpf.write('\n'.join(articles))
        tmpf.flush()
        subprocess.call(['less', '-XRF', tmpf.name])
