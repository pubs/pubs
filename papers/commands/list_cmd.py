from .. import files
from .. import pretty

import subprocess
import tempfile

def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser

def command(config):
    papers = files.read_papers()

    articles = []
    for p in papers.options('papers'):
        filename = papers.get('papers', p)
        number = p[1:]
        bibdata = files.load_bibdata(filename + '.bibyaml')
        bibdesc = pretty.bib_oneliner(bibdata)
        articles.append('{:3d}   {}'.format(int(number), bibdesc))

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=True) as tmpf:
        tmpf.write('\n'.join(articles))
        tmpf.flush()
        subprocess.call(['less', '-XRF', tmpf.name])
