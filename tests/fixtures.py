# -*- coding: utf-8 -*-

import dotdot
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

franny_bibdata  = coder.decode_bibdata(franny_bib)
franny_bibentry = franny_bibdata['Franny1961']

doe_bibdata     = coder.decode_bibdata(doe_bib)
doe_bibentry    = doe_bibdata['Doe2013']

turing_bibdata  = coder.decode_bibdata(str_fixtures.turing_bib)
turing_bibentry = turing_bibdata['turing1950computing']
turing_metadata = coder.decode_metadata(str_fixtures.turing_meta)

page_bibdata    = coder.decode_bibdata(str_fixtures.bibtex_raw0)
page_bibentry   = page_bibdata['Page99']
page_metadata   = coder.decode_metadata(str_fixtures.metadata_raw0)

page_metadata   = coder.decode_metadata(str_fixtures.metadata_raw0)
