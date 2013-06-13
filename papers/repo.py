import os
import shutil
import glob

from . import files
from .paper import PaperInRepo, NoDocumentFile
from . import color
from . import configs


ALPHABET = 'abcdefghijklmopqrstuvwxyz'
BASE_FILE = 'papers.yaml'
BIB_DIR = 'bibdata'
META_DIR = 'meta'
DOC_DIR = 'doc'


class CiteKeyAlreadyExists(Exception):
    pass


class Repository(object):

    def __init__(self, config=None):
        self.papersdir = None
        self.citekeys = []
        if config is None:
            config = configs.CONFIG
        self.config = config

    def has_paper(self, citekey):
        return citekey in self.citekeys

    def paper_from_citekey(self, citekey):
        """Load a paper by its citekey from disk, if necessary."""
        return PaperInRepo.load(
                self, self.path_to_paper_file(citekey, 'bib'),
                metapath=self.path_to_paper_file(citekey, 'meta'))

    def citekey_from_ref(self, ref, fatal=True):
        """Tries to get citekey from given ref.
        Ref can be a citekey or a number.
        """
        if ref in self.citekeys:
            return ref
        else:
            try:
                return self.citekeys[int(ref)]
            except (IndexError, ValueError):
                if fatal:
                    print('{}: no paper with reference {}'.format(
                          color.dye('error', color.error)
                          color.dye(ref, color.citekey)))
                    exit(-1)
                raise(IOError('file not found'))

    def paper_from_ref(self, ref, fatal=True):
        key = self.citekey_from_ref(ref, fatal=fatal)
        return self.paper_from_citekey(key)

    # creating new papers

    def add_paper(self, p):
        if p.citekey is None:  # TODO also test if citekey is valid
            raise(ValueError("Invalid citekey: %s." % p.citekey))
        elif self.has_paper(p.citekey):
            raise(ValueError("Citekey already exists in repository: %s"
                    % p.citekey))
        self.citekeys.append(p.citekey)
        # write paper files
        self.save_paper(p)
        # update repository files
        self.save()
        # TODO change to logging system (17/12/2012)
        print "Added: %s" % p.citekey

    def add_or_update(self, paper):
        if not self.has_paper(paper.citekey):
            self.add_paper(paper)
        else:
            self.save_paper(paper)

    def update(self, paper, old_citekey=None, overwrite=False):
        """Updates a paper, eventually changing its citekey.
        The paper should be in repository. If the citekey changes,
        the new citekey should be free except if the overwrite argument
        is set to True.
        """
        if old_citekey is None:
            old_citekey = paper.citekey
        if old_citekey not in self.citekeys:
            raise(ValueError, 'Paper not in repository. Add first')
        else:
            if paper.citekey == old_citekey:
                self.save_paper(paper)
            else:
                if self.has_paper(paper.citekey):
                    if not overwrite:
                        raise(CiteKeyAlreadyExists,
                            "There is already a paper with citekey: %s."
                                % paper.citekey)
                    else:
                        self.save_paper(paper)
                else:
                    self.add_paper(paper)
                # Eventually move document file
                paper = PaperInRepo.from_paper(paper, self)
                try:
                    path = self.find_document(old_citekey)
                    self.import_document(paper.citekey, path)
                except NoDocumentFile:
                    pass
                self.remove(old_citekey)

    def remove(self, citekey):
        paper = self.paper_from_citekey(citekey)
        self.citekeys.remove(citekey)
        self.save()
        for f in ('bib', 'meta'):
            os.remove(self.path_to_paper_file(citekey, f))
        # Eventually remove associated document
        try:
            path = paper.get_document_path_in_repo()
            os.remove(path)
        except NoDocumentFile:
            pass

    def save_paper(self, paper):
        if not self.has_paper(paper.citekey):
            raise(ValueError('Paper not in repository, first add it.'))
        paper.save_to_disc(self.path_to_paper_file(paper.citekey, 'bib'),
                self.path_to_paper_file(paper.citekey, 'meta'))

    def get_free_citekey(self, paper, citekey=None):
        """Create a unique citekey for the given paper.
        """
        if citekey is None:
            citekey = paper.generate_citekey()
        num = []
        while citekey + _to_suffix(num) in self.citekeys:
            _str_incr(num)
        return citekey + _to_suffix(num)

    def base_file_path(self):
        return os.path.join(self.papersdir, 'papers.yaml')

    def size(self):
        return len(self.citekeys)

    def save(self):
        papers_config = {'citekeys': self.citekeys}
        files.write_yamlfile(self.base_file_path(), papers_config)

    def load(self):
        papers_config = files.read_yamlfile(self.base_file_path())
        self.citekeys = papers_config['citekeys']

    def init(self, papersdir):
        self.papersdir = papersdir
        os.makedirs(os.path.join(self.papersdir, BIB_DIR))
        os.makedirs(os.path.join(self.papersdir, META_DIR))
        doc_dir = self.get_document_directory()
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)
        self.save()

    def path_to_paper_file(self, citekey, file_):
        if file_ == 'bib':
            return os.path.join(self.papersdir, BIB_DIR, citekey + '.bibyaml')
        elif file_ == 'meta':
            return os.path.join(self.papersdir, META_DIR, citekey + '.meta')
        else:
            raise(ValueError("%s is not a valid paper file." % file_))

    def get_document_directory(self):
        if self.config.has_option(configs.MAIN_SECTION, 'document-directory'):
            doc_dir = self.config.get(configs.MAIN_SECTION,
                                      'document-directory')
        else:
            doc_dir = os.path.join(self.papersdir, DOC_DIR)
        return files.clean_path(doc_dir)

    def find_document(self, citekey):
        doc_dir = self.get_document_directory()
        found = glob.glob(doc_dir + "/%s.*" % citekey)
        if found:
            return found[0]
        else:
            raise NoDocumentFile

    def all_papers(self):
        for key in self.citekeys:
            yield self.paper_from_citekey(key)

    def import_document(self, citekey, doc_file):
        if citekey not in self.citekeys:
            raise(ValueError, "Unknown citekey: %s." % citekey)
        else:
            doc_path = self.get_document_directory()
            if not (os.path.exists(doc_path) and os.path.isdir(doc_path)):
                raise(NoDocumentFile,
                      "Document directory %s, does not exist." % doc_path)
            ext = os.path.splitext(doc_file)[1]
            new_doc_file = os.path.join(doc_path, citekey + ext)
            shutil.copy(doc_file, new_doc_file)

    def get_labels(self):
        labels = set()
        for p in self.all_papers():
            labels = labels.union(p.metadata.get('labels', []))
        return labels

    @classmethod
    def from_directory(cls, config, papersdir=None):
        repo = cls(config=config)
        if papersdir is None:
            papersdir = config.get(configs.MAIN_SECTION, 'papers-directory')
        repo.papersdir = files.clean_path(papersdir)
        repo.load()
        return repo


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
