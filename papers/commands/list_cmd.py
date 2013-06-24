from .. import pretty
from .. import repo
from .. import color


def parser(subparsers, config):
    parser = subparsers.add_parser('list', help="list papers")
    parser.add_argument('-k', '--citekeys-only', action='store_true',
            default=False, dest='citekeys',
            help='Only returns citekeys of matching papers.')
    parser.add_argument('query', nargs='*',
            help='Paper query (e.g. "year: 2000" or "labels: math")')
    return parser


def command(config, ui, citekeys, query):
    rp = repo.Repository.from_directory(config)
    papers = [(n, p) for n, p in enumerate(rp.all_papers())
              if test_paper(query, p)]
    if citekeys:
        paper_strings = [p.citekey for n, p in papers]
    else:
        paper_strings = []
        for n, p in papers:
            bibdesc = pretty.bib_oneliner(p.bibentry)
            paper_strings.append((u'{num:d}: [{citekey}] {descr} {labels}'.format(
                num=int(n),
                citekey=color.dye(p.citekey, color.purple),
                descr=bibdesc,
                labels=color.dye(' '.join(p.metadata.get('labels', [])),
                                 color.purple, bold=True),
                )).encode('utf-8'))
    ui.print_('\n'.join(paper_strings))


# TODO author is not implemented, should we do it by last name only or more
# complex
# TODO implement search by type of document
def test_paper(query_string, p):
    for test in query_string:
        tmp = test.split(':')
        if len(tmp) != 2:
            raise ValueError('command not valid')

        field = tmp[0]
        value = tmp[1]

        if field in ['labels', 'l', 'tags', 't']:
            if value not in p.metadata['labels']:
                return False
        elif field in ['author', 'authors', 'a']:  # that is the very ugly
            if not 'author' in p.bibentry.persons:
                return False
            a = False
            for p in p.bibentry.persons['author']:
                if value in p.last()[0]:
                    a = True
            return a
        elif field in p.bibentry.fields:
                if value not in p.bibentry.fields[field]:
                    return False
        else:
            return False
    return True
