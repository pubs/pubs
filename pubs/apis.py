"""Interface for Remote Bibliographic APIs"""

import requests
import feedparser
from bs4 import BeautifulSoup
from uis import get_ui


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
        ui = get_ui()
        ui.error('malformed arXiv ID: {}'.format(arxiv_id))
    if 'arxiv_doi' in entry:
        return doi2bibtex(entry['arxiv_doi'])
    else:
        # Create a bibentry from the metadata.
        bibtext = '@misc{{{},\n'.format(arxiv_id)
        bibtext += 'Author = {'
        for i, author in enumerate(entry['authors']):
            bibtext += author['name']
            if i < len(entry['authors']) - 1:
                bibtext += ' and '
        bibtext += '},\n'
        bibtext += 'Title = {{{}}},\n'.format(entry['title'].strip('\n'))
        bibtext += 'Year = {{{}}},\n'.format(entry['published_parsed'].tm_year)
        bibtext += 'Eprint = {{arXiv:{}}},\n'.format(arxiv_id)
        bibtext += '}'
        return bibtext
