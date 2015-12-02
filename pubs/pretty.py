# display formatting

from . import color
from .bibstruct import TYPE_KEY


# should be adaptated to bibtexparser dicts
def person_repr(p):
    raise NotImplementedError
    return ' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s)


def short_authors(bibdata):
    try:
        authors = [p for p in bibdata['author']]
        if len(authors) < 3:
            return ' and '.join(authors)
        else:
            return authors[0] + (' et al.' if len(authors) > 1 else '')
    except KeyError:  # When no author is defined
        return ''


def bib_oneliner(bibdata):
    authors = short_authors(bibdata)
    journal = ''
    if 'journal' in bibdata:
        journal = ' ' + bibdata['journal']['name']
    elif bibdata[TYPE_KEY] == 'inproceedings':
        journal = ' ' + bibdata.get('booktitle', '')

    return u'{authors} \"{title}\"{journal}{year}'.format(
        authors=color.dye_out(authors, 'bold'),
        title=bibdata.get('title', ''),
        journal=color.dye_out(journal, 'italic'),
        year=' ({})'.format(bibdata['year']) if 'year' in bibdata else '',
        )


def bib_desc(bib_data):
    article = bib_data[list(bib_data.keys())[0]]
    s = '\n'.join('author: {}'.format(p)
            for p in article['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.items())
    return s


def paper_oneliner(p, citekey_only=False):
    if citekey_only:
        return p.citekey
    else:
        bibdesc = bib_oneliner(p.bibdata)
        tags = '' if len(p.tags) == 0 else '| {}'.format(
            ','.join(color.dye_out(t, color.tag) for t in sorted(p.tags)))
        return u'[{citekey}] {descr} {tags}'.format(
            citekey=color.dye_out(p.citekey, 'purple'),
            descr=bibdesc, tags=tags)
