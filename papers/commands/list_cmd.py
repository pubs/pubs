from .. import files
from .. import pretty
from .. import color

import subprocess
import tempfile

def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser

def command(config):
    papers = files.load_papers()

    articles = []
    for p in papers.options('citekeys'):
        number = p[2:]
        citekey = papers.get('citekeys', p)
        filename = papers.get('papers', citekey)
        bibdata = files.load_bibdata(filename + '.bibyaml')
        bibdesc = pretty.bib_oneliner(bibdata)
        articles.append('{:3d} {}{}{}{}   {}'.format(int(number), color.purple, citekey, color.end, (8-len(citekey))*' ', bibdesc))

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=True) as tmpf:
        tmpf.write('\n'.join(articles))
        tmpf.flush()
        subprocess.call(['less', '-XRF', tmpf.name])
