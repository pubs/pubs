# -*- coding: utf-8 -*-

from pybtex.database import Person

import testenv
from pubs import endecoder
import str_fixtures

coder = endecoder.EnDecoder()

franny_bib = """
@article{
    Franny1961,
    author = "Salinger, J. D.",
    title = "Franny and Zooey",
    year = "1961",
}

"""

doe_bib = """
@article{
    Doe2013,
    author = "Doe, John",
    title = "Nice Title",
    year = "2013",
}

"""


franny_bibdata = coder.decode_bibdata(franny_bib)
doe_bibdata    = coder.decode_bibdata(doe_bib)


# bibdata = coder.decode_bibdata(str_fixtures.bibtex_external0, fmt='bibtex')
# page99 = Paper(bibdata)




# turing1950 = Paper()
# turing1950.bibentry.fields['title'] = u'Computing machinery and intelligence.'
# turing1950.bibentry.fields['year'] = u'1950'
# turing1950.bibentry.persons['author'] = [Person(u'Alan Turing')]
# turing1950.citekey = turing1950.generate_citekey()
# turing1950.tags = ['computer', 'AI']
