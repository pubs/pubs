import os
import shutil
import glob
import itertools

from . import files
from .paper import PaperInRepo, NoDocumentFile
from . import configs



BASE_FILE = 'papers.yaml'
BIB_DIR = 'bibdata'
META_DIR = 'meta'
DOC_DIR = 'doc'


class CiteKeyCollision(Exception):
    pass


class InvalidReference(Exception):
    pass


class Repository(object):

    def __init__(self, config, load = True):
        """Initialize the repository.

        :param load:  if load is True, load the repository from disk,
                      from path config.papers_dir.
        """
        self.config = config
        self.citekeys = []
        if load:
            self.load()

    # @classmethod
    # def from_directory(cls, config, papersdir=None):
    #     repo = cls(config)
    #     if papersdir is None:
    #         papersdir = config.papers_dir
    #     repo.papersdir = files.clean_path(papersdir)
    #     repo.load()
    #     return repo

    def __contains__(self, citekey):
        """Allows to use 'if citekey in repo' pattern"""
        return citekey in self.citekeys

    def __len__(self):
        return len(self.citekeys)


    # load, save repo

    def _init_dirs(self, autodoc = True):
        """Create, if necessary, the repository directories.

        Should only be called by load or save.
        """
        self.bib_dir  = files.clean_path(self.config.papers_dir, BIB_DIR)
        self.meta_dir = files.clean_path(self.config.papers_dir, META_DIR)
        if self.config.doc_dir == 'doc':
            self.doc_dir = files.clean_path(self.config.papers_dir, DOC_DIR)
        else:
            self.doc_dir  = files.clean_path(self.config.doc_dir)
        self.cfg_path = files.clean_path(self.config.papers_dir, 'papers.yaml')

        for d in [self.bib_dir, self.meta_dir, self.doc_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def load(self):
        """Load the repository, creating dirs if necessary"""
        self._init_dirs()
        repo_config = files.read_yamlfile(self.cfg_path)
        self.citekeys = repo_config['citekeys']

    def save(self):
        """Save the repo, creating dirs if necessary"""
        self._init_dirs()
        repo_cfg = {'citekeys': self.citekeys}
        files.write_yamlfile(self.cfg_path, repo_cfg)


    # reference

    def ref2citekey(self, ref):
        """Tries to get citekey from given reference.
        Ref can be a citekey or a number.
        """
        if ref in self.citekeys:
            return ref
        else:
            try:
                return self.citekeys[int(ref)]
            except (IndexError, ValueError):
                raise(InvalidReference)


    # papers

    def all_papers(self):
        for key in self.citekeys:
            yield self.get_paper(key)

    def get_paper(self, citekey):
        """Load a paper by its citekey from disk, if necessary."""
        return PaperInRepo.load(self, self._bibfile(citekey),
                                      self._metafile(citekey))


    # add, remove papers

    def add_paper(self, p, overwrite = False):
        if p.citekey is None:  # TODO also test if citekey is valid
            raise(ValueError("Invalid citekey: %s." % p.citekey))
        if not overwrite and p.citekey in self:
            raise CiteKeyCollision('citekey {} already in use'.format(
                                   p.citekey))
        self.citekeys.append(p.citekey)
        self.save_paper(p)
        self.save()
        # TODO change to logging system (17/12/2012)
        print('Added: {}'.format(p.citekey))
        return p

    def rename_paper(self, paper, new_citekey, overwrite=False):
        """Modify the citekey of a paper, and propagate changes to disk"""
        if paper.citekey not in self:
            raise ValueError(
                  'paper {} not in repository'.format(paper.citekey))
        if (not overwrite and paper.citekey != new_citekey
            and new_citekey in self):
            raise CiteKeyCollision('citekey {} already in use'.format(
                                   new_citekey))
        self.remove_paper(paper.citekey, remove_doc = False)
        paper.citekey = new_citekey
        self.add_paper(paper, overwrite = overwrite)

    def _bibfile(self, citekey):
        return os.path.join(self.bib_dir, citekey + '.bibyaml')

    def _metafile(self, citekey):
        return os.path.join(self.meta_dir, citekey + '.meta')

    def remove_paper(self, citekey, remove_doc = True):
        paper = self.get_paper(citekey)
        self.citekeys.remove(citekey)
        os.remove(self._metafile(citekey))
        os.remove(self._bibfile(citekey))

        # Eventually remove associated document
        if remove_doc:
            try:
                path = paper.get_document_path_in_repo()
                os.remove(path)
            except NoDocumentFile:
                pass

        self.save()

    def save_paper(self, paper):
        if not paper.citekey in self:
            raise(ValueError('Paper not in repository, first add it.'))
        paper.save(self._bibfile(paper.citekey),
                   self._metafile(paper.citekey))

    def generate_citekey(self, paper, citekey=None):
        """Create a unique citekey for the given paper."""
        if citekey is None:
            citekey = paper.generate_citekey()
        for n in itertools.count():
            if not citekey + _base27(n) in self.citekeys:
                return citekey + _base27(n)

    def import_document(self, citekey, doc_file):
        if citekey not in self.citekeys:
            raise ValueError("Unknown citekey {}.".format(citekey))
        else:
            if not os.path.isfile(doc_file):
                raise ValueError("No file {} found.".format(doc_file))
            new_doc_file = os.path.join(self.doc_dir,
                                        os.path.basename(doc_file))
            shutil.copy(doc_file, new_doc_file)

    def get_tags(self):
        tags = set()
        for p in self.all_papers():
            tags = tags.union(p.tags)
        return tags




def _base27(n):
    return _base27((n-1) // 26) + chr(97+((n-1)% 26)) if n else ''

def _base(num, b):
    q, r = divmod(num - 1, len(b))
    return _base(q, b) + b[r] if num else ''
