# display formatting

import color

def person_repr(p):
    return u' '.join(s for s in [u' '.join(p.first(abbr = True)),
                                 u' '.join(p.middle(abbr = True)),
                                 u' '.join(p.prelast(abbr = False)),
                                 u' '.join(p.last(abbr = False)),
                                 u' '.join(p.lineage(abbr = True))] if s)

def bib_oneliner(bib_data):
    article = bib_data.entries[list(bib_data.entries.keys())[0]]
    authors = ', '.join(person_repr(p) for p in article.persons['author'])
    title = article.fields['title']
    year = article.fields.get('year', '')
    journal = ''
    field = 'journal'
    if article.type == 'inproceedings':
        field = 'booktitle'
    journal = article.fields.get(field, '')
    return u'{}{}{} \"{}{}{}\" {}{}{} {}({}{}{}){}'.format(
            color.green, authors, color.grey, color.bcyan, title, color.grey,
            color.yellow, journal, color.end, color.grey, color.end, year,
            color.grey, color.end)

def bib_desc(bib_data):
    article = bib_data.entries[list(bib_data.entries.keys())[0]]
    s  = u'\n'.join(u'author: {}'.format(person_repr(p)) for p in article.persons['author'])
    s += u'\n'
    s += u'\n'.join(u'{}: {}'.format(k, v) for k, v in article.fields.items())
    return s
