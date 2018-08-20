import os
import time

from . import databroker


class CacheEntry(object):

    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp


class CacheEntrySet(object):

    def __init__(self, databroker, name):
        self.databroker = databroker
        self.name = name
        if name == 'metacache':
            self._pull_fun = databroker.pull_metadata
            self._push_fun = databroker.push_metadata
            self._mtime_fun = databroker.filebroker.mtime_metafile
        elif name == 'bibcache':
            self._pull_fun = databroker.pull_bibentry
            self._push_fun = databroker.push_bibentry
            self._mtime_fun = databroker.filebroker.mtime_bibfile
        else:
            raise ValueError
        self._entries = None
        self.modified = False
        # does the filesystem supports subsecond stat time?
        self.nsec_support = os.stat('.').st_mtime != int(os.stat('.').st_mtime)

    @property
    def entries(self):
        if self._entries is None:
            self._entries = self._try_pull_cache()
        return self._entries

    def flush(self, force=False):
        if force or self.modified:
            self.databroker.push_cache(self.name, self.entries)
            self.modified = False

    def pull(self, citekey):
        if self._is_outdated(citekey):
            # if we get here, we must update the cache.
            t = time.time()
            data = self._pull_fun(citekey)
            self.entries[citekey] = CacheEntry(data, t)
            self.modified = True
        return self.entries[citekey].data

    def push(self, citekey, data):
        self._push_fun(citekey, data)
        self.push_to_cache(citekey, data)

    def push_to_cache(self, citekey, data):
        """Push to cash only."""
        mtime = self._mtime_fun(citekey)
        self.entries[citekey] = CacheEntry(data, mtime)
        self.modified = True

    def remove_from_cache(self, citekey):
        """Removes from cache only."""
        if citekey in self.entries:
            self.entries.pop(citekey)
            self.modified = True

    def _try_pull_cache(self):
        try:
            return self.databroker.pull_cache(self.name)
        except Exception:  # take no prisonners; if something is wrong, no cache.
            return {}

    def _is_outdated(self, citekey):
        if citekey in self.entries:
            mtime = self._mtime_fun(citekey)
            boundary = mtime if self.nsec_support else mtime + 1
            return self.entries[citekey].timestamp < boundary
        else:
            return True


class DataCache(object):
    """ DataCache class, provides a very similar interface as DataBroker

        Has two roles :
        1. Provides a buffer between the commands and the hard drive.
           Until a command request a hard drive ressource, it does not touch it.
        2. Keeps an up-to-date, pickled version of the repository, to speed up things
           when they are a lot of files. Update are also done only when required.
           Changes are detected using data modification timestamps.
    """
    def __init__(self, pubsdir, docsdir, create=False):
        self.pubsdir = pubsdir
        self.docsdir = docsdir
        self._databroker = None
        self._metacache = None
        self._bibcache = None
        if create:
            self._create()

    def close(self):
        self.flush_cache()

    @property
    def databroker(self):
        if self._databroker is None:
            self._databroker = databroker.DataBroker(self.pubsdir, self.docsdir,
                                                     create=False)
        return self._databroker

    @property
    def metacache(self):
        if self._metacache is None:
            self._metacache = CacheEntrySet(self.databroker, 'metacache')
        return self._metacache

    @property
    def bibcache(self):
        if self._bibcache is None:
            self._bibcache = CacheEntrySet(self.databroker, 'bibcache')
        return self._bibcache

    def _create(self):
        self._databroker = databroker.DataBroker(self.pubsdir, self.docsdir,
                                                 create=True)

    def flush_cache(self, force=False):
        """Write cache to disk"""
        self.metacache.flush(force=force)
        self.bibcache.flush(force=force)

    def pull_metadata(self, citekey):
        return self.metacache.pull(citekey)

    def pull_bibentry(self, citekey):
        return self.bibcache.pull(citekey)

    def push_metadata(self, citekey, metadata):
        self.metacache.push(citekey, metadata)

    def push_bibentry(self, citekey, bibdata):
        self.bibcache.push(citekey, bibdata)

    def push(self, citekey, metadata, bibdata):
        self.databroker.push(citekey, metadata, bibdata)
        self.metacache.push_to_cache(citekey, metadata)
        self.bibcache.push_to_cache(citekey, bibdata)

    def remove(self, citekey):
        self.databroker.remove(citekey)
        self.metacache.remove_from_cache(citekey)
        self.bibcache.remove_from_cache(citekey)

    def exists(self, citekey, meta_check=False):
        return self.databroker.exists(citekey, meta_check=meta_check)

    def citekeys(self):
        return self.databroker.citekeys()

    def listing(self, filestats=True):
        return self.databroker.listing(filestats=filestats)

    # docbroker

    def in_docsdir(self, docpath):
        return self.databroker.in_docsdir(docpath)

    def real_docpath(self, docpath):
        return self.databroker.real_docpath(docpath)

    def add_doc(self, citekey, source_path, overwrite=False):
        return self.databroker.add_doc(citekey, source_path, overwrite=overwrite)

    def remove_doc(self, docpath, silent=True):
        return self.databroker.remove_doc(docpath, silent=silent)

    def rename_doc(self, docpath, new_citekey):
        return self.databroker.rename_doc(docpath, new_citekey)

    # notesbroker

    def real_notepath(self, citekey, extension):
        return self.databroker.real_notepath(citekey, extension)

    def remove_note(self, citekey, extension, silent=True):
        return self.databroker.remove_note(citekey, extension, silent=True)

    def rename_note(self, old_citekey, new_citekey, extension):
        return self.databroker.rename_note(old_citekey, new_citekey, extension)
