import files
import color

from paper import Paper


ALPHABET = 'abcdefghijklmopqrstuvwxyz'


class Repository(object):

    def __init__(self, paperdir=None):
        if paperdir:
            self.paperdir = paperdir
        else:
            self.paperdir = files.find_papersdir()
        self.papers_config = files.load_papers()
        self.citekeys = self.papers_config['citekeys']

    # loading existing papers

    def paper_from_number(self, number, fatal = True):
        try:
            citekey = self.citekeys[int(number)]
            paper = self.paper_from_citekey(citekey)
            return paper
        except KeyError:
            if fatal:
                print('{}error{}: no paper with number {}{}{}'.format(
                    color.error, color.normal, color.citekey, citekey, color.end))
                exit(-1)
            raise IOError, 'file not found'
            
    def paper_from_citekey(self, citekey, fatal=True):
        """Load a paper by its citekey from disk, if necessary."""
        try:
            return Paper.from_disc(citekey)
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
    
    def add_paper_from_paths(self, pdfpath, bibpath):
        p = Paper.from_bibpdffiles(pdfpath, bibpath)
        self.add_paper(p)

    def add_paper(self, p):
        # updating papersconfig
        bib_data_entry = p.bib_data.entries[list(p.bib_data.entries.keys())[0]]
        p.citekey = self.get_valid_citekey(bib_data_entry)

        self.papers_config['citekeys'].append(p.citekey)
        self.citekeys.append(p.citekey)

        # writing all to disk
        p.save_to_disc()
        files.save_papers(self.papers_config)
        print "Added: %s" % p.citekey
        return p

    def add_papers(self, bibpath):
        bib_data = Paper.import_bibdata(bibpath)
        for k in bib_data.entries:
            sub_bib = type(bib_data)(preamble=bib_data._preamble)
            sub_bib.add_entry(k, bib_data.entries[k])
            name, meta = Paper.create_meta(sub_bib, pdfpath=None)
            p = Paper(name, bib_data = sub_bib, metadata = meta)
            self.add_paper(p)

    def get_valid_citekey(self, entry):
        citekey = str2citekey(entry.key)
        if citekey in self.citekeys:
            raise(ValueError, "An entry with same citekey already exists.")
        if len(citekey) == 0:
            citekey = self.create_citekey(entry)
        return citekey

    def create_citekey(self, entry, allowed = tuple()):
        """Create a cite key unique to a given bib_data.
        
        Raises:
            KeyError if no author is defined.
        """
        author_key = 'author'
        if not 'author' in entry.persons:
            author_key = 'editor'
        try:
            first_author = entry.persons[author_key][0]
        except KeyError:
            raise(ValueError,
                    'No author or editor defined: cannot generate a citekey.')
        try:
            year = entry.fields['year']
        except KeyError:
            year = ''
        prefix = u'{}{}'.format(first_author.last()[0][:6], year)
        prefix = str2citekey(prefix)
        # Normalize chars and remove non-ascii
        prefix = unicodedata.normalize('NFKD', prefix
                ).encode('ascii', 'ignore')
        letter = 0
        citekey = prefix
        while citekey in self.citekeys and citekey not in allowed:
            citekey = prefix + ALPHABET[letter]
            letter += 1
        return citekey

    def size(self):
        return len(self.citekeys)
