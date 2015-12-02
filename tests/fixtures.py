# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import dotdot
from pubs import endecoder
import str_fixtures

coder = endecoder.EnDecoder()

franny_bib = """@article{Franny1961,
    author = "Salinger, J. D.",
    title = "Franny and Zooey",
    year = "1961",
}
"""

doe_bib = """
@article{Doe2013,
    author = "Doe, John",
    title = "Nice Title",
    year = "2013",
}
"""

dummy_metadata = {'docfile': 'docsdir://hop.la', 'tags': set(['a', 'b'])}

franny_bibentry = coder.decode_bibdata(franny_bib)
franny_bibdata  = franny_bibentry['Franny1961']

doe_bibentry    = coder.decode_bibdata(doe_bib)
doe_bibdata     = doe_bibentry['Doe2013']

turing_bibentry = coder.decode_bibdata(str_fixtures.turing_bib)
turing_bibdata  = turing_bibentry['turing1950computing']
turing_metadata = coder.decode_metadata(str_fixtures.turing_meta)

page_bibentry   = coder.decode_bibdata(str_fixtures.bibtex_raw0)
page_bibdata    = page_bibentry['Page99']
page_metadata   = coder.decode_metadata(str_fixtures.metadata_raw0)

page_metadata   = coder.decode_metadata(str_fixtures.metadata_raw0)
