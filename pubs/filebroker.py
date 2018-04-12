import os
import re
from .p3 import urlparse, u_maybe

from .content import (check_file, check_directory, read_text_file, write_file,
                      system_path, check_content, copy_content)

from . import content


META_EXT = '.yaml'
BIB_EXT  = '.bib'


def filter_filename(filename, ext):
    """ Return the filename without the extension if the extension matches ext.
        Otherwise return None
    """
    pattern = '.*\{}$'.format(ext)
    if re.match(pattern, filename) is not None:
        return u_maybe(filename[:-len(ext)])


class FileBroker(object):
    """ Handles all access to meta and bib files of the repository.

        * Does *absolutely no* encoding/decoding.
        * Communicate failure with exceptions.
    """

    def __init__(self, directory, create=False):
        self.directory = os.path.expanduser(directory)
        self.metadir   = os.path.join(self.directory, 'meta')
        self.bibdir    = os.path.join(self.directory, 'bib')
        self.cachedir  = os.path.join(self.directory, '.cache')
        if create:
            self._create()
        check_directory(self.directory)
        check_directory(self.metadir)
        check_directory(self.bibdir)
        # cache directory is created (if absent) if other directories exists.
        if not check_directory(self.cachedir, fail=False):
            os.mkdir(system_path(self.cachedir))

    def _create(self):
        """Create meta and bib directories if absent"""
        if not check_directory(self.directory, fail=False):
            os.mkdir(system_path(self.directory))
        if not check_directory(self.metadir, fail=False):
            os.mkdir(system_path(self.metadir))
        if not check_directory(self.bibdir, fail=False):
            os.mkdir(system_path(self.bibdir))

    def bib_path(self, citekey):
        return os.path.join(self.bibdir, citekey + BIB_EXT)

    def meta_path(self, citekey):
        return os.path.join(self.metadir, citekey + META_EXT)

    def pull_cachefile(self, filename):
        filepath = os.path.join(self.cachedir, filename)
        return content.read_binary_file(filepath)

    def push_cachefile(self, filename, data):
        filepath = os.path.join(self.cachedir, filename)
        write_file(filepath, data, mode='wb')

    def mtime_metafile(self, citekey):
        try:
            filepath = self.meta_path(citekey)
            return os.path.getmtime(filepath)
        except OSError:
            raise IOError("'{}' not found.".format(filepath))

    def mtime_bibfile(self, citekey):
        try:
            filepath = self.bib_path(citekey)
            return os.path.getmtime(filepath)
        except OSError:
            raise IOError("'{}' not found.".format(filepath))

    def pull_metafile(self, citekey):
        return read_text_file(self.meta_path(citekey))

    def pull_bibfile(self, citekey):
        return read_text_file(self.bib_path(citekey))

    def push_metafile(self, citekey, metadata):
        """Put content to disk. Will gladly override anything standing in its way."""
        write_file(self.meta_path(citekey), metadata)

    def push_bibfile(self, citekey, bibdata):
        """Put content to disk. Will gladly override anything standing in its way."""
        write_file(self.bib_path(citekey), bibdata)

    def push(self, citekey, metadata, bibdata):
        """Put content to disk. Will gladly override anything standing in its way."""
        self.push_metafile(citekey, metadata)
        self.push_bibfile(citekey, bibdata)

    def remove(self, citekey):
        metafilepath = self.meta_path(citekey)
        if check_file(metafilepath):
            os.remove(system_path(metafilepath))
        bibfilepath = self.bib_path(citekey)
        if check_file(bibfilepath):
            os.remove(system_path(bibfilepath))

    def exists(self, citekey, meta_check=False):
        """ Checks wether the bibtex of a citekey exists.

            :param meta_check:  if True, will return if both the bibtex and the meta file exists.
        """
        does_exists = check_file(self.bib_path(citekey), fail=False)
        if meta_check:
            meta_exists = check_file(self.meta_path(citekey), fail=False)
            does_exists = does_exists and meta_exists
        return does_exists

    def listing(self, filestats=True):
        metafiles = []
        for filename in os.listdir(system_path(self.metadir)):
            citekey = filter_filename(filename, META_EXT)
            if citekey is not None:
                if filestats:
                    stats = os.stat(system_path(os.path.join(self.metadir, filename)))
                    metafiles.append(citekey, stats)
                else:
                    metafiles.append(citekey)

        bibfiles = []
        for filename in os.listdir(system_path(self.bibdir)):
            citekey = filter_filename(filename, BIB_EXT)
            if citekey is not None:
                if filestats:
                    stats = os.stat(system_path(os.path.join(self.bibdir, filename)))
                    bibfiles.append(citekey, stats)
                else:
                    bibfiles.append(citekey)

        return {'metafiles': metafiles, 'bibfiles': bibfiles}


class DocBroker(object):
    """ DocBroker manages the document files optionally attached to the papers.

        * only one document can be attached to a paper (might change in the future)
        * this document can be anything, the content is never processed.
        * these document have an adress of the type "docsdir://citekey.pdf"
        * docsdir:// correspond to /path/to/pubsdir/doc (configurable)
        * document outside of the repository will not be removed.
        * move_doc only applies from inside to inside the docsdir
    """

    def __init__(self, directory, scheme='docsdir', subdir='doc'):
        self.scheme = scheme
        self.docdir = os.path.join(directory, subdir)
        if not check_directory(self.docdir, fail=False):
            os.mkdir(system_path(self.docdir))

    def in_docsdir(self, docpath):
        try:
            parsed = urlparse(docpath)
        except Exception:
            return False
        return parsed.scheme == self.scheme

    # def doc_exists(self, citekey, ext='.txt'):
    #     return check_file(os.path.join(self.docdir, citekey + ext), fail=False)

    def real_docpath(self, docpath):
        """ Return the full path
            Essentially transform pubsdir://doc/{citekey}.{ext} to /path/to/pubsdir/doc/{citekey}.{ext}.
            Return absoluted paths of regular ones otherwise.
        """
        if self.in_docsdir(docpath):
            parsed = urlparse(docpath)
            if parsed.path == '':
                docpath = os.path.join(self.docdir, parsed.netloc)
            else:
                docpath = os.path.join(self.docdir, parsed.netloc, parsed.path[1:])
        return docpath

    def add_doc(self, citekey, source_path, overwrite=False):
        """ Add a document to the docsdir, and return its location.

            The document will be named {citekey}.{ext}.
            The location will be docsdir://{citekey}.{ext}.
            :param overwrite: will overwrite existing file.
            :return: the above location
        """
        full_source_path = self.real_docpath(source_path)
        check_content(full_source_path)

        target_path = '{}://{}'.format(self.scheme, citekey + os.path.splitext(source_path)[-1])
        full_target_path = self.real_docpath(target_path)
        copy_content(full_source_path, full_target_path, overwrite=overwrite)
        return target_path

    def remove_doc(self, docpath, silent=True):
        """ Will remove only file hosted in docsdir://

            :raise ValueError: for other paths, unless :param silent: is True
        """
        if not self.in_docsdir(docpath):
            if not silent:
                raise ValueError(('the file to be removed {} is set as external. '
                                  'you should remove it manually.').format(docpath))
            return
        filepath = self.real_docpath(docpath)
        if check_file(filepath):
            os.remove(system_path(filepath))

    def rename_doc(self, docpath, new_citekey):
        """ Move a document inside the docsdir

            :raise IOError: if docpath doesn't point to a file
                            if new_citekey doc exists already.
            :raise ValueError: if docpath is not in docsdir().

            if an exception is raised, the files on disk haven't changed.
        """
        if not self.in_docsdir(docpath):
            raise ValueError('cannot rename an external file ({}).'.format(docpath))

        new_docpath = self.add_doc(new_citekey, docpath)
        self.remove_doc(docpath)

        return new_docpath
