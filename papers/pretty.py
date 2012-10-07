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
    year = article.fields['year']
    journal = article.fields['journal']
    return '{}{}{} \"{}{}{}\" {}{}{} {}({}{}{}){}'.format(
            color.green, authors, color.grey, color.bcyan, title, color.grey,
            color.yellow, journal, color.end, color.grey, color.end, year,
            color.grey, color.end)

def bib_desc(bib_data):
    article = bib_data.entries[list(bib_data.entries.keys())[0]]
    s  = '\n'.join('author: {}'.format(person_repr(p)) for p in article.persons['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.fields.items())
    return s

alphabet = 'abcdefghijklmopqrstuvwxyz'

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import files

def create_citekey(bib_data):
    """Create a cite key unique to the paper"""
    article = bib_data.entries[list(bib_data.entries.keys())[0]]
    first_author = article.persons['author'][0]
    year = article.fields['year']
    prefix = '{}{}'.format(first_author.last()[0][:6], year[2:])

    papers = files.load_papers()
    letter = 0, False
    citekey = None
    
    citekey = prefix
    while not letter[1]:
        try:
            papers.get('papers', citekey)
            citekey = prefix + alphabet[letter[0]]
            letter = letter[0]+1, False
        except configparser.NoOptionError:
            letter = letter[0], True

    return citekey
