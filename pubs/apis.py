"""Interface for Remote Bibliographic APIs"""
import re
import datetime

import requests
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
import feedparser
from bs4 import BeautifulSoup

from . import endecoder


class ReferenceNotFoundError(Exception):
    pass


def get_bibentry_from_api(id_str, id_type, try_doi=True, ui=None):
    """Return a bibtex string from various ID methods.

    This is a wrapper around functions that will return a bibtex string given
    one of:

    * DOI
    * IBSN
    * arXiv ID

    Args:
        id_str: A string with the ID.
        id_type: Name of the ID type.  Must be one of `doi`, `isbn`, or `arxiv`.
        rp: A `Repository` object.
        ui: A UI object.

    Returns:
        A bibtex string.

    Raises:
        ValueError: if `id_type` is not one of `doi`, `isbn`, or `arxiv`.
        apis.ReferenceNotFoundError: if no valid reference could be found.
    """

    id_fns = {
        'doi': doi2bibtex,
        'isbn': isbn2bibtex,
        'arxiv': arxiv2bibtex,
    }

    id_type = id_type.lower()
    if id_type not in id_fns.keys():
        raise ValueError('id_type must be one of `doi`, `isbn`, or `arxiv`.')

    bibentry_raw = id_fns[id_type](id_str, try_doi=try_doi, ui=ui)
    bibentry = endecoder.EnDecoder().decode_bibdata(bibentry_raw)
    if bibentry is None:
        raise ReferenceNotFoundError(
            'invalid {} {} or unable to retrieve bibfile from it.'.format(id_type, id_str))
    return bibentry



def _get_request(url, headers=None):
    """GET requests to a url. Return the `requests` object.

    :raise ConnectionError:  if anything goes bad (connection refused, timeout
                             http status error (401, 404, etc)).
    """
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        raise ReferenceNotFoundError(e.args)


    ## DOI support

def doi2bibtex(doi, **kwargs):
    """Return a bibtex string from a DOI"""

    url = 'https://dx.doi.org/{}'.format(doi)
    headers = {'accept': 'application/x-bibtex'}
    r = _get_request(url, headers=headers)
    if r.encoding is None:
        r.encoding = 'utf8'  # Do not rely on guessing from request

    return r.text


    ## ISBN support


def isbn2bibtex(isbn, **kwargs):
    """Return a bibtex string from an ISBN"""

    url = 'https://www.ottobib.com/isbn/{}/bibtex'.format(isbn)
    r = _get_request(url)
    soup = BeautifulSoup(r.text, "html.parser")
    citation = soup.find("textarea").text

    if len(citation) == 0:
        raise ReferenceNotFoundError("No information could be retrieved about ISBN '{}'. ISBN databases are notoriously incomplete. If the ISBN is correct, you may have to enter information manually by invoking 'pubs add' without the '-I' argument.".format(isbn))

    return citation

    # Note: apparently ottobib.com uses caracter modifiers for accents instead
    # of the correct unicode characters. TODO: Should we convert them?


    ## arXiv support

_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
           'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

def _is_arxiv_oldstyle(arxiv_id):
    return re.match(r"(arxiv\:)?[a-z\-]+\/[0-9]+(v[0-9]+)?", arxiv_id.lower()) is not None

def _extract_arxiv_id(entry):
    pattern = r"http[s]?://arxiv.org/abs/(?P<entry_id>.+)"
    return re.search(pattern, entry['id']).groupdict()['entry_id']


def arxiv2bibtex(arxiv_id, try_doi=True, ui=None):
    """Return a bibtex string from an arXiv ID

    :param arxiv_id: arXiv id, with or without the `arXiv:` prefix and version
                     suffix (e.g. `v1`). Old an new style are accepted. Here are
                     example of accepted identifiers: `1510.00322`,
                     `arXiv:1510.00322`, `0901.0512`, `arXiv:0901.0512`,
                     `hep-ph/9409201` or `arXiv:hep-ph/9409201`.
                     Note that the `arXiv:` prefix will be automatically
                     removed, and the version suffix automatically added if
                     missing.
    :param try_doi:  if a DOI is referenced in the arXiv metadata,
                     try to download it instead. If that fails for any reason,
                     falls back to the arXiv, with a warning message, if the
                     UI is provided.
    :param ui:       if not None, will display a warning if the doi request
                     fails.
    """
    ## handle errors
    url = 'https://export.arxiv.org/api/query?id_list={}'.format(arxiv_id)
    try:
        r = requests.get(url)
        if r.status_code == 400:  # bad request
            msg = ("the arXiv server returned a bad request error. The "
                   "arXiv id {} is possibly invalid or malformed.".format(arxiv_id))
            raise ReferenceNotFoundError(msg)
        r.raise_for_status()  # raise an exception for HTTP errors:
                              # 401, 404, 400 if `ui` is None, etc.
    except requests.exceptions.RequestException as e:
        msg = ("connection error while retrieving arXiv data for "
               "'{}': {}".format(arxiv_id, e))
        raise ReferenceNotFoundError(msg)

    feed = feedparser.parse(r.text)
    if len(feed.entries) == 0:  # no results.
        msg = "no results for arXiv id {}".format(arxiv_id)
        raise ReferenceNotFoundError(msg)
    if len(feed.entries) > 1:  # I don't know how that could happen, but let's
                               # be ready for it.
        results = '\n'.join('{}. {}'.format(i, entry['title'])
                            for entry in feed.entries)
        msg = ("multiple results for arXiv id {}:\n{}\nThis is unexpected. "
               "Please submit an issue at "
               "https://github.com/pubs/pubs/issues").format(arxiv_id, choices)
        raise ReferenceNotFoundError(msg)

    entry = feed.entries[0]

    ## try to return a doi instead of the arXiv reference
    if try_doi and 'arxiv_doi' in entry:
        try:
            return doi2bibtex(entry['arxiv_doi'])
        except ReferenceNotFoundError as e:
            if ui is not None:
                ui.warning(str(e))

    ## create a bibentry from the arXiv response.
    db = BibDatabase()
    entry_id = _extract_arxiv_id(entry)
    author_str = ' and '.join(
        [author['name'] for author in entry['authors']])
    db.entries = [{
        'ENTRYTYPE': 'article',
        'ID': entry_id,
        'author': author_str,
        'title': entry['title'],
        'year': str(entry['published_parsed'].tm_year),
        'month': _months[entry['published_parsed'].tm_mon-1],
        'eprint': entry_id,
        'eprinttype': 'arxiv',
        'date': entry['published'], # not really standard, but a resolution more
                                    # granular than months is increasinlgy relevant.
        'url': entry['link'],
        'urldate': datetime.datetime.utcnow().isoformat() + 'Z' # can't hurt.
    }]
    # we don't add eprintclass for old-style ids, as it is in the id already.
    if not _is_arxiv_oldstyle(entry_id):
        db.entries[0]['eprintclass'] = entry['arxiv_primary_category']['term']
    if 'arxiv_doi' in entry:
        db.entries[0]['arxiv_doi'] = entry['arxiv_doi']

    bibtex = bibtexparser.dumps(db)
    return bibtex
