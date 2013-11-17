# -*- coding: utf-8 -*-

from pybtex.database import Person

import testenv
from pubs import endecoder
import str_fixtures

coder = endecoder.EnDecoder()

franny_bib = """@article{Franny1961,
    author = "Salinger, J. D.",
    title = "Franny and Zooey",
    year = "1961"}
"""

doe_bib = """
@article{Doe2013,
    author = "Doe, John",
    title = "Nice Title",
    year = "2013"}
"""

franny_bibdata = coder.decode_bibdata(franny_bib)
doe_bibdata    = coder.decode_bibdata(doe_bib)
page_bibdata   = coder.decode_bibdata(str_fixtures.bibtex_raw0)
turing_bibdata = coder.decode_bibdata(str_fixtures.turing_bib)
