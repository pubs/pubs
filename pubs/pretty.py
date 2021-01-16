from __future__ import unicode_literals

import os
import re

from . import color
from .bibstruct import TYPE_KEY


CHARS = re.compile('[{}\n\t\r]')


def sanitize(s):
    return CHARS.sub('', s)


# should be adaptated to bibtexparser dicts
def person_repr(p):
    raise NotImplementedError
    return ' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s)


def short_authors(bibdata, max_authors=3):
    """
    :param max_authors:  number of authors to display completely. Additional authors will be
                       represented by 'et al.'.
    """
    try:
        authors = [p for p in bibdata.persons['author']]
        if 0 < max_authors < len(authors):
            authors_str = '{} et al.'.format(authors[0])
        else:
            authors_str = ' and '.join(authors)
        return authors_str
    except KeyError:  # When no author is defined
        return ''


def bib_oneliner(bibdata, max_authors=3):
    authors = short_authors(bibdata, max_authors=max_authors)
    journal = ''
    if 'journal' in bibdata:
        journal = ' ' + bibdata['journal']
    elif bibdata[TYPE_KEY] == 'inproceedings':
        journal = ' ' + bibdata.get('booktitle', '')

    return sanitize('{authors} \"{title}\"{journal}{year}'.format(
        authors=color.dye_out(authors, 'author'),
        title=color.dye_out(bibdata.get('title', ''), 'title'),
        journal=color.dye_out(journal, 'publisher'),
        year=' ({})'.format(color.dye_out(bibdata['year'], 'year'))
             if 'year' in bibdata else ''
    ))


def bib_desc(bib_data):
    article = bib_data[list(bib_data.keys())[0]]
    s = '\n'.join('author: {}'.format(p)
                  for p in article['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.items())
    return s


def paper_oneliner(p, citekey_only=False, max_authors=3):
    if citekey_only:
        return p.citekey
    else:
        bibdesc = bib_oneliner(p.get_unicode_bibdata(), max_authors=max_authors)
        doc_str = ''
        if p.docpath is not None:
            doc_extension = os.path.splitext(p.docpath)[1]
            doc_str = color.dye_out(
                ' [{}]'.format(doc_extension[1:] if len(doc_extension) > 1
                               else 'NOEXT'),
                'tag')
        tags = '' if len(p.tags) == 0 else '| {}'.format(
            ','.join(color.dye_out(t, 'tag') for t in sorted(p.tags)))
        return '[{citekey}] {descr}{doc} {tags}'.format(
            citekey=color.dye_out(p.citekey, 'citekey'),
            descr=bibdesc, tags=tags, doc=doc_str)
