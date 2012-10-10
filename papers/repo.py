try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from paper import Paper

alphabet = 'abcdefghijklmopqrstuvwxyz'


class Repository(object):

    def __init__(self):
        self.paperdir = files.find_papersdir()
        self.papers_config = files.load_papers()
        self.citekeys = dict(ck, None for ck in self.paper_config.options('citekeys')
        self.numbers = sorted(n[2:] for n in self.paper_config.options('numbers'))

    # loading existing papers

    def paper_from_number(self, number, fatal = True):
        try:
            citekey = self.papers_config.get('numbers', 'ck'+number)
            return self.load_paper(citekey)
        except configparser.NoOptionError:
            if fatal:
                print('{}error{}: no paper with number {}{}{}'.format(
                    color.error, color.normal, color.citekey, citekey, color.end)
                exit(-1)
            raise IOError, 'file not found'
            
    def paper_from_citekey(self, citekey, fatal = True):
        """Load a paper by its citekey from disk, if necessary."""
        try:
            paper = self.citekeys[citekey]
            if paper is None:
                name = self.papers_config.get('citekeys', citekey)
                paper =  Paper.from_disc(name)
                self.citekeys[citekey] = paper
                return paper
        except KeyError:
            if fatal:
                print('{}error{}: no paper with citekey {}{}{}'.format(
                       color.error, color.normal, color.citekey, citekey, color.end)
                exit(-1)
            raise IOError, 'file not found'

    def paper_from_any(self, key, fatal = True):
        try:
            return rp.paper_from_citekey(key, fatal = False)
        except IOError:
            try:
                return rp.paper_from_number(key, fatal = False)
            except IOError:
                if fatal:
                    print('{}error{}: paper with citekey or number {}{}{} not found{}'.format(
                        color.error, color.normal, color.citekey, key, color.normal, color.end))
                    exit(-1)
                raise IOError, 'file not found'

    # creating new papers
    
    def add_paper(self, pdffile, bibfile):
        
        fullpdfpath = os.path.abspath(pdffile)
        fullbibpath = os.path.abspath(bibfile)
        files.check_file(fullpdfpath)
        files.check_file(fullbibpath)
        
        name, ext = os.path.splitext(os.path.split(fullpdfpath)[1])
        if ext != '.pdf' and ext !=   '.ps':
            print('{}warning{}: extension {}{}{} not recognized{}'.format(
                   color.yellow, color.grey, color.cyan, ext, color.grey, color.end))
        
        # creating meta file
        meta = create_meta(fullpdfpath, name, ext, bib_data)
        
        # creating bibyaml file
        bib_data = files.load_externalbibfile(fullbibpath)
        print('{}bibliographic data present in {}{}{}'.format(
               color.grey, color.cyan, bibfile, color.end))
        print(pretty.bib_desc(bib_data))
        
        # updating papersconfig    
        citekey = pretty.create_citekey(bib_data)
        papers.set('citekeys', citekey, name)
        papers.set('numbers', 'ck' + count, citekey)
        
        # writing all to disk
        files.write_bibdata(bib_data, name)
        files.write_papers(papers)
        files.write_meta(meta, name)

    def create_meta(self, path, name, ext, bib_data):
        citekey = create_citekey(bib_data, allowed = (,))
        number = create_number()
        
        meta = configparser.ConfigParser()
        meta.add_section('metadata')
        
        meta.set('metadata', 'name', name)
        meta.set('metadata', 'extension', ext)
        meta.set('metadata', 'path', os.path.normpath(fullpdfpath))
        
        meta.add_section('notes')
        
        return meta

    def create_citekey(self, bib_data, allowed = (,)):
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
        
    def create_number(self, bib_data, allowed = []):
        count = self.papers_config.get('header', 'count')
        self.papers_config.set('header', 'count', count + 1)
        return count
        