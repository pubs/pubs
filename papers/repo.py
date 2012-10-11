try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import files
import color
from paper import Paper

alphabet = 'abcdefghijklmopqrstuvwxyz'


class Repository(object):

    def __init__(self):
        self.paperdir = files.find_papersdir()
        self.papers_config = files.load_papers()
        self.citekeys = dict((ck, name) for ck, name in self.papers_config.items('citekeys'))
        self.numbers = sorted(n[2:] for n in self.papers_config.options('numbers'))

    # loading existing papers

    def paper_from_number(self, number, fatal = True):
        try:
            citekey = self.papers_config.get('numbers', 'ck'+number)
            return self.paper_from_citekey(citekey)
        except configparser.NoOptionError:
            if fatal:
                print('{}error{}: no paper with number {}{}{}'.format(
                    color.error, color.normal, color.citekey, citekey, color.end))
                exit(-1)
            raise IOError, 'file not found'
            
    def paper_from_citekey(self, citekey, fatal = True):
        """Load a paper by its citekey from disk, if necessary."""
        try:
            paper = self.citekeys[citekey]
            if paper is None:
                name = self.papers_config.get('citekeys', citekey)
            paper =  Paper.from_disc(name, citekey = citekey)
            self.citekeys[citekey] = paper
            return paper
        except KeyError:
            if fatal:
                print('{}error{}: no paper with citekey {}{}{}'.format(
                       color.error, color.normal, color.citekey, citekey, color.end))
                exit(-1)
            raise IOError, 'file not found'

    def paper_from_any(self, key, fatal = True):
        try:
            return self.paper_from_citekey(key, fatal = False)
        except IOError:
            try:
                return self.paper_from_number(key, fatal = False)
            except IOError:
                if fatal:
                    print('{}error{}: paper with citekey or number {}{}{} not found{}'.format(
                        color.error, color.normal, color.citekey, key, color.normal, color.end))
                    exit(-1)
                raise IOError, 'file not found'

    # creating new papers
    
    def add_paper(self, pdfpath, bibpath):
        
        p = Paper.from_bibpdffiles(pdfpath, bibpath)        

        # updating papersconfig
        p.citekey = self.create_citekey(p.bib_data)
        p.number  = self.create_number()

        self.papers_config.set('citekeys', p.citekey, p.name)
        self.papers_config.set('numbers', 'ck' + str(p.number), p.citekey)

        self.citekeys[p.citekey] = p.name
        self.numbers.append(str(p.number))
        self.numbers.sort()
               
        # writing all to disk
        files.write_papers(self.papers_config)
        p.save_to_disc()

        return p

    def create_citekey(self, bib_data, allowed = tuple()):
        """Create a cite key unique to a given bib_data"""
        article = bib_data.entries[list(bib_data.entries.keys())[0]]
        first_author = article.persons['author'][0]
        year = article.fields['year']
        prefix = '{}{}'.format(first_author.last()[0][:6], year[2:])

        letter = 0, False
        citekey = None

        citekey = prefix
        while citekey in self.citekeys and citekey not in allowed:
            citekey = prefix + alphabet[letter[0]]
            letter += 1

        return citekey
        
    def create_number(self):
        count = self.papers_config.getint('header', 'count')
        self.papers_config.set('header', 'count', count + 1)
        return count