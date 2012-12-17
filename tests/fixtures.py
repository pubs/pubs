from pybtex.database import Person

from papers.paper import Paper


turing1950 = Paper()
turing1950.bibentry.fields['title'] = u'Computing machinery and intelligence.'
turing1950.bibentry.fields['year'] = u'1950'
turing1950.bibentry.persons['author'] = [Person(u'Alan Turing')]
turing1950.citekey = turing1950.generate_citekey()


doe2013 = Paper()
doe2013.bibentry.fields['title'] = u'Nice title.'
doe2013.bibentry.fields['year'] = u'2013'
doe2013.bibentry.persons['author'] = [Person(u'John Doe')]
doe2013.citekey = doe2013.generate_citekey()
