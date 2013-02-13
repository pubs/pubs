import subprocess
import tempfile

from .. import pretty
from ..color import colored
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser


def command(config, ui):
    rp = repo.Repository.from_directory()
    articles = []
    for n, p in enumerate(rp.all_papers()):
        bibdesc = pretty.bib_oneliner(p.bibentry)
        articles.append((u'{num:d}: [{citekey}] {descr}'.format(
            num=int(n),
            citekey=colored(rp.citekeys[n], 'purple'),
            descr=bibdesc,
            )).encode('utf-8'))

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=True) as tmpf:
        tmpf.write('\n'.join(articles))
        tmpf.flush()
        subprocess.call(['less', '-XRF', tmpf.name])
