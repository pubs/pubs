from pybtex.database import Person

from papers.paper import Paper


turing1950 = Paper()
turing1950.bibentry.fields['title'] = u'Computing machinery and intelligence.'
turing1950.bibentry.fields['year'] = u'1950'
turing1950.bibentry.persons['author'] = [Person(u'Alan Turing')]
turing1950.citekey = turing1950.generate_citekey()
turing1950.tags = ['computer', 'AI']


doe2013 = Paper()
doe2013.bibentry.fields['title'] = u'Nice title.'
doe2013.bibentry.fields['year'] = u'2013'
doe2013.bibentry.persons['author'] = [Person(u'John Doe')]
doe2013.citekey = doe2013.generate_citekey()


pagerankbib = """
@techreport{Page99,
     number = {1999-66},
      month = {November},
     author = {Lawrence Page and Sergey Brin and Rajeev Motwani and Terry Winograd},
       note = {Previous number = SIDL-WP-1999-0120},
      title = {The PageRank Citation Ranking: Bringing Order to the Web.},
       type = {Technical Report},
  publisher = {Stanford InfoLab},
       year = {1999},
institution = {Stanford InfoLab},
        url = {http://ilpubs.stanford.edu:8090/422/},
}
"""

pagerankbib_generated = """@techreport{
    Page99,
    author = "Page, Lawrence and Brin, Sergey and Motwani, Rajeev and Winograd, Terry",
    publisher = "Stanford InfoLab",
    title = "The PageRank Citation Ranking: Bringing Order to the Web.",
    url = "http://ilpubs.stanford.edu:8090/422/",
    number = "1999-66",
    month = "November",
    note = "Previous number = SIDL-WP-1999-0120",
    year = "1999",
    institution = "Stanford InfoLab"
}

"""