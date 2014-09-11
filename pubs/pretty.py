# display formatting

from . import color


# should be adaptated to bibtexparser dicts
def person_repr(p):
    raise NotImplementedError
    return ' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s)


def short_authors(bibentry):
    try:
        authors = [p for p in bibentry['author']]
        if len(authors) < 3:
            return ', '.join(authors)
        else:
            return authors[0] + (' et al.' if len(authors) > 1 else '')
    except KeyError:  # When no author is defined
        return ''


def bib_oneliner(bibentry):
    authors = short_authors(bibentry)
    journal = ''
    if 'journal' in bibentry:
        journal = ' ' + bibentry['journal']['name']
    elif bibentry['type'] == 'inproceedings':
        journal = ' ' + bibentry.get('booktitle', '')

    return u'{authors} \"{title}\"{journal}{year}'.format(
            authors=color.dye(authors, color.cyan),
            title=bibentry['title'],
            journal=color.dye(journal, color.yellow),
            year=' ({})'.format(bibentry['year']) if 'year' in bibentry else '',
            )


def bib_desc(bib_data):
    article = bib_data[list(bib_data.keys())[0]]
    s = '\n'.join('author: {}'.format(p)
            for p in article['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.items())
    return s


def paper_oneliner(p, citekey_only = False):
    if citekey_only:
        return p.citekey
    else:
        bibdesc = bib_oneliner(p.bibentry)
        return u'[{citekey}] {descr} {tags}'.format(
            citekey=color.dye(p.citekey, color.purple),
            descr=bibdesc,
            tags=color.dye(' '.join(sorted(p.tags)),
                           color.tag, bold=False),
            )
