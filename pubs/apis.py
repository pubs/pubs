"""Interface for Remote Bibliographic APIs"""

import requests
from bs4 import BeautifulSoup

def doi2bibtex(doi):
    """Return a bibtex string of metadata from a DOI"""

    url = 'http://dx.doi.org/{}'.format(doi)
    headers = {'accept': 'application/x-bibtex'}
    r = requests.get(url, headers=headers)

    return r.text

def isbn2bibtex(isbn):
    """Return a bibtex string of metadata from a DOI"""

    url = 'http://www.ottobib.com/isbn/{}/bibtex'.format(isbn)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    citation = soup.find("textarea").text

    return citation
