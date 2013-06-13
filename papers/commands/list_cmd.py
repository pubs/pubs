from .. import pretty
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('cmd', nargs='*', help='experimental option "year: 2000 or labels: bite"')
    return parser


def command(config, ui, cmd):
    rp = repo.Repository.from_directory(config)
    articles = []
    for n, p in enumerate(rp.all_papers()):
        if test_paper(cmd, p):
            bibdesc = pretty.bib_oneliner(p.bibentry)
            articles.append((u'{num:d}: [{citekey}] {descr} {labels}'.format(
                num=int(n),
                citekey=color.dye(rp.citekeys[n], color.purple),
                descr=bibdesc,
                labels=color.dye(' '.join(p.metadata.get('labels', [])),
                                 color.purple),
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

        if field in ['labels', 'l', 'tags', 't']:
            if value not in p.metadata['labels']:
                return False
        elif field in ['authors', 'a']:  # that is the very ugly
            if not 'author' in p.bibentry.persons:
                return False
            a = False
            for p in p.bibentry.persons['author']:
                if value in p.last()[0]:
                    a = True
            return a
        else:
            if field in p.bibentry.fields:
                if value not in p.bibentry.fields[field]:
                    return False
            else:
                return False
    return True
