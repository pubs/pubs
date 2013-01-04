# display formatting

from color import colored
from pybtex.bibtex.utils import bibtex_purify


def person_repr(p):
    return bibtex_purify(' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.middle(abbr=True)),
        ' '.join(p.prelast(abbr=False)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s))


def short_authors(bibentry):
    authors = [person_repr(p) for p in bibentry.persons['author']]
    if len(authors) < 3:
        return ', '.join(authors)
    else:
        return authors[0] + (' et al.' if len(authors) > 1 else '')


def bib_oneliner(bibentry):
    authors = short_authors(bibentry)
    title = bibtex_purify(bibentry.fields['title'])
    year = bibtex_purify(bibentry.fields.get('year', ''))
    journal = ''
    field = 'journal'
    if bibentry.type == 'inproceedings':
        field = 'booktitle'
    journal = bibtex_purify(bibentry.fields.get(field, ''))
    return u'{authors} \"{title}\" {journal} ({year})'.format(
            authors=colored(authors, 'green'),
            title=title,
            journal=colored(journal, 'yellow'),
            year=year,
            )


def bib_desc(bib_data):
    article = bib_data.entries[list(bib_data.entries.keys())[0]]
    s = '\n'.join('author: {}'.format(person_repr(p))
            for p in article.persons['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.fields.items())
    return s
