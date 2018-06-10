import itertools
from datetime import datetime

from . import bibstruct
from . import events
from .datacache import DataCache
from .paper import Paper
from .content import system_path


def _base27(n):
    return _base27((n - 1) // 26) + chr(ord('a') + ((n - 1) % 26)) if n else ''


class CiteKeyError(Exception):

    default_message = "Wrong citekey: {}."

    def __init__(self, citekey, message=None):
        self.message = message
        self.citekey = citekey

    def __str__(self):
        return self.message or self.default_message.format(self.citekey)


class CiteKeyCollision(CiteKeyError):

    default_message = "Citekey already in use: {}."


class CiteKeyNotFound(CiteKeyError):

    default_message = "No entry found for citekey: {}."


class Repository(object):

    def __init__(self, conf, create=False):
        self.conf = conf
        self._citekeys = None
        self.databroker = DataCache(self.conf['main']['pubsdir'],
                                    self.conf['main']['docsdir'], create=create)

    def close(self):
        self.databroker.close()

    @property
    def citekeys(self):
        if self._citekeys is None:
            self._citekeys = self.databroker.citekeys()
        return self._citekeys

    def __contains__(self, citekey):
        """ Allows to use 'if citekey in repo' pattern

        The convention is that the paper is in the repository
        if and only if a bibfile is in the repository.
        """
        return self.databroker.exists(citekey)

    def __len__(self):
        """Warning: costly the first time."""
        return len(self.citekeys)

    # papers
    def all_papers(self):
        for key in self.citekeys:
            yield self.pull_paper(key)

    def citekeys_from_prefix(self, prefix):
        """Return all citekey beginning with prefix."""
        return tuple(citekey for citekey in self.citekeys
                     if citekey.startswith(prefix))

    def pull_paper(self, citekey):
        """Load a paper by its citekey from disk, if necessary."""
        if citekey in self:
            return Paper.from_bibentry(
                self.databroker.pull_bibentry(citekey),
                citekey=citekey,
                metadata=self.databroker.pull_metadata(citekey))
        else:
            raise CiteKeyNotFound(citekey)

    def push_paper(self, paper, overwrite=False, event=True):
        """ Push a paper to disk

            :param overwrite:  if False, mimick the behavior of adding a paper
                               if True, mimick the behavior of updating a paper
        """
        bibstruct.check_citekey(paper.citekey)
        if (not overwrite) and (paper.citekey in self):
            raise CiteKeyCollision(paper.citekey)
        if not paper.added:
            paper.added = datetime.now()
        self.databroker.push_bibentry(paper.citekey, paper.bibentry)
        self.databroker.push_metadata(paper.citekey, paper.metadata)
        self.citekeys.add(paper.citekey)
        if event:
            events.AddEvent(paper.citekey).send()

    def remove_paper(self, citekey, remove_doc=True, event=True):
        """ Remove a paper. Is silent if nothing needs to be done."""
        if event:
            events.RemoveEvent(citekey).send()
        if remove_doc:
            self.remove_doc(citekey, detach_only=True)
        try:
            self.databroker.remove_note(citekey, self.conf['main']['note_extension'],
                                        silent=True)
        except IOError:
            # FIXME: if IOError is about being unable to
            # remove the file, we need to issue an error.
            pass
        self.citekeys.remove(citekey)
        self.databroker.remove(citekey)

    def remove_doc(self, citekey, detach_only=False):
        """ Remove a doc. Is silent if nothing needs to be done."""
        try:
            metadata = self.databroker.pull_metadata(citekey)
            docpath = metadata.get('docfile')
            self.databroker.remove_doc(docpath, silent=True)
            if not detach_only:
                p = self.pull_paper(citekey)
                p.docpath = None
                self.push_paper(p, overwrite=True, event=False)
        except IOError:
            # FIXME: if IOError is about being unable to
            # remove the file, we need to issue an error.I
            pass

    def pull_docpath(self, citekey):
        try:
            p = self.pull_paper(citekey)
            return self.databroker.real_docpath(p.docpath)
        except IOError:
            # FIXME: if IOError is about being unable to
            # remove the file, we need to issue an error.I
            pass

    def rename_paper(self, paper, new_citekey=None, old_citekey=None):
        """Move a paper from a citekey to another one.

        Even if the new and old citekey are the same, the paper instance is
        pushed to disk.

        :return:  True if a rename happened, False if not.
        """
        if old_citekey is None:
            old_citekey = paper.citekey
        if new_citekey is None:
            new_citekey = paper.citekey
        paper.citekey = new_citekey
        # check if new_citekey is not the same as paper.citekey
        if old_citekey == new_citekey:
            self.push_paper(paper, overwrite=True, event=False)
            return False
        else:
            # check if new_citekey does not exists
            if new_citekey in self:
                msg = "Can't rename paper to {}, citekey already exists.".format(new_citekey)
                raise CiteKeyCollision(new_citekey, message=msg)

            # move doc file if necessary
            if self.databroker.in_docsdir(paper.docpath):
                paper.docpath = self.databroker.rename_doc(paper.docpath, new_citekey)

            # move note file if necessary
            try:
                self.databroker.rename_note(old_citekey, new_citekey,
                                            self.conf['main']['note_extension'])
            except IOError:
                pass

            self.push_paper(paper, event=False)
            # remove_paper of old_citekey
            self.remove_paper(old_citekey, event=False)
            # send event
            events.RenameEvent(paper, old_citekey).send()
            return True

    def push_doc(self, citekey, docfile, copy=None):
        p = self.pull_paper(citekey)
        if copy is None:
            copy = self.conf['main']['doc_add'] in ('copy', 'move')
        if copy:
            docfile = self.databroker.add_doc(citekey, docfile)
        else:
            docfile = system_path(docfile)
        p.docpath = docfile
        self.push_paper(p, overwrite=True, event=False)

    def unique_citekey(self, base_key):
        """Create a unique citekey for a given basekey."""
        for n in itertools.count():
            if not base_key + _base27(n) in self.citekeys:
                return base_key + _base27(n)

    def get_tags(self):
        """FIXME: bibdata doesn't need to be read."""
        tags = set()
        for p in self.all_papers():
            tags = tags.union(p.tags)
        return tags
