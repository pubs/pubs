from .. import pretty
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('devlist', help="list papers")
    parser.add_argument('cmd', nargs='*', help='experimental option "year: 2000 or labels: bite"')
    return parser


def command(config, ui, cmd):
    rp = repo.Repository.from_directory(config)
    articles = []
    for n, p in enumerate(rp.all_papers()):
        if test_paper(cmd, p):
            bibdesc = pretty.bib_oneliner(p.bibentry, color=ui.color)
            articles.append((u'{num:d}: [{citekey}] {descr} {labels}'.format(
                num=int(n),
                citekey=ui.colored(rp.citekeys[n], 'purple'),
                descr=bibdesc,
                labels=ui.colored(' '.join(p.metadata.get('labels', [])),
                                  'purple'),
                )).encode('utf-8'))
    ui.print_('\n'.join(articles))


# TODO author is not implemented, should we do it by last name only or more
# complex
# TODO implement search by type of document
def test_paper(tests, p):
    for test in tests:
        tmp = test.split(':')
        if len(tmp) != 2:
            raise ValueError('command not valid')

        field = tmp[0]
        value = tmp[1]

        if field == 'labels':
            if value not in p.metadata['labels']:
                return False
        else:
            if field in p.bibentry.fields:
                if value not in p.bibentry.fields[field]:
                    return False
            else:
                return False
    return True
