"""Interface for Remote Bibliographic APIs"""

import requests

def doi2bibtex(doi):
  """Return a bibtex string of metadata from a DOI"""

  url = 'http://dx.doi.org/{}'.format(doi)
  headers = {'accept': 'application/x-bibtex'}
  r = requests.get(url, headers=headers)

  return r.text
