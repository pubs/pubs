from .. import pretty
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list all papers")
    return parser


def command(config, ui):
    rp = repo.Repository.from_directory(config)
    articles = []
    for n, p in enumerate(rp.all_papers()):
        bibdesc = pretty.bib_oneliner(p.bibentry, color=ui.color)
        articles.append((u'{num:d}: [{citekey}] {descr} {labels}'.format(
            num=int(n),
            citekey=ui.colored(rp.citekeys[n], 'purple'),
            descr=bibdesc,
            labels=ui.colored(''.join(p.metadata.get('labels', [])), 'purple'),
            )).encode('utf-8'))
    ui.print_('\n'.join(articles))
