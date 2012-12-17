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

    def paper_from_number(self, number, fatal=True):
        try:
            citekey = self.citekeys[int(number)]
            paper = self.paper_from_citekey(citekey)
            return paper
        except KeyError:
            if fatal:
                print('{}error{}: no paper with number {}{}{}'.format(
                    color.error, color.normal, color.citekey, citekey,
                    color.end))
                exit(-1)
            raise(IOError, 'file not found')

    def paper_from_citekey(self, citekey, fatal=True):
        """Load a paper by its citekey from disk, if necessary."""
        try:
            return Paper.load(citekey)
        except KeyError:
            if fatal:
                print('{}error{}: no paper with citekey {}{}{}'.format(
                       color.error, color.normal, color.citekey, citekey,
                       color.end))
                exit(-1)
            raise(IOError, 'file not found')

    def paper_from_any(self, key, fatal=True):
        try:
            return self.paper_from_citekey(key, fatal=False)
        except IOError:
            try:
                return self.paper_from_number(key, fatal=False)
            except IOError:
                if fatal:
                    print('{}error{}: paper with citekey or number {}{}{} not found{}'.format(
                        color.error, color.normal, color.citekey, key, color.normal, color.end))
                    exit(-1)
                raise(IOError, 'file not found')

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
        # TODO Update by giving filename (17/12/2012)
        p.save_to_disc()
        files.save_papers(self.papers_config)
        print "Added: %s" % p.citekey
        return p

    def add_papers(self, bibpath):
        bib_data = Paper.import_bibdata(bibpath)
        for k in bib_data.entries:
            sub_bib = type(bib_data)(preamble=bib_data._preamble)
            sub_bib.add_entry(k, bib_data.entries[k])
            meta = Paper.create_meta(pdfpath=None)
            name = meta['filename']
            p = Paper(name, bib_data=sub_bib, metadata=meta)
            self.add_paper(p)

    def get_free_citekey(self, paper, citekey=None):
        """Create a unique citekey for the given paper.
        """
        if citekey is None:
            citekey = paper.generate_citekey()
        suffix = ''
        while citekey + suffix in self.citekeys:
            _str_incr(suffix)
        return citekey + suffix

    def size(self):
        return len(self.citekeys)


def _char_incr(c):
    return chr(ord(c) + 1)


def _str_incr(l):
    """Increment a number in a list string representation.

    Numbers are represented in base 26 with letters as digits.
    """
    pos = 0
    while pos < len(l):
        if l[pos] == 'z':
            l[pos] = 'a'
            pos += 1
        else:
            l[pos] = _char_incr(l[pos])
            return
    l.append('a')


def _to_suffix(l):
    return ''.join(l[::-1])
