# display formatting

from color import colored
from pybtex.bibtex.utils import bibtex_purify


# A bug in pybtex makes the abbreviation wrong here
# (Submitted with racker ID: ID: 3605659)
# The purification should also be applied to names but unfortunately
# it removes dots which is annoying on abbreviations.
def person_repr(p):
    return ' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s)


def short_authors(bibentry):
    try:
        authors = [person_repr(p) for p in bibentry.persons['author']]
        if len(authors) < 3:
            return ', '.join(authors)
        else:
            return authors[0] + (' et al.' if len(authors) > 1 else '')
    except KeyError:  # When no author is defined
        return ''


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
            authors=colored(authors, 'cyan'),
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
