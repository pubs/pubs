"""Interface for Remote Bibliographic APIs"""

import requests
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
import feedparser
from bs4 import BeautifulSoup


class ReferenceNotFoundException(Exception):
    pass


def doi2bibtex(doi):
    """Return a bibtex string of metadata from a DOI"""

    url = 'http://dx.doi.org/{}'.format(doi)
    headers = {'accept': 'application/x-bibtex'}
    r = requests.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = 'utf8'  # Do not rely on guessing from request

    return r.text


def isbn2bibtex(isbn):
    """Return a bibtex string of metadata from an ISBN"""

    url = 'http://www.ottobib.com/isbn/{}/bibtex'.format(isbn)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    citation = soup.find("textarea").text

    return citation


def arxiv2bibtex(arxiv_id):
    """Return a bibtex string of metadata from an arXiv ID"""

    url = 'https://export.arxiv.org/api/query?id_list=' + arxiv_id
    r = requests.get(url)
    feed = feedparser.parse(r.text)
    entry = feed.entries[0]

    if 'title' not in entry:
        raise ReferenceNotFoundException('arXiv ID not found.')
    elif 'arxiv_doi' in entry:
        bibtex = doi2bibtex(entry['arxiv_doi'])
    else:
        # Create a bibentry from the metadata.
        db = BibDatabase()
        author_str = ' and '.join(
            [author['name'] for author in entry['authors']])
        db.entries = [{
            'ENTRYTYPE': 'misc',
            'ID': arxiv_id,
            'author': author_str,
            'title': entry['title'],
            'year': str(entry['published_parsed'].tm_year),
            'Eprint': arxiv_id,
        }]
        bibtex = bibtexparser.dumps(db)
    return bibtex
