# display formatting

import color

def person_repr(p):
    return ' '.join(s for s in [' '.join(p.first(abbr = True)),
                                 ' '.join(p.middle(abbr = True)),
                                 ' '.join(p.prelast(abbr = False)),
                                 ' '.join(p.last(abbr = False)),
                                 ' '.join(p.lineage(abbr = True))] if s)

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
    s  = '\n'.join('author: {}'.format(person_repr(p)) for p in article.persons['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.fields.items())
    return s
