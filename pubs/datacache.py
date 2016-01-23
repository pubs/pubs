import os
import time

from . import databroker


class CacheEntry(object):

    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp


class DataCache(object):
    """ DataCache class, provides a very similar interface as DataBroker

        Has two roles :
        1. Provides a buffer between the commands and the hard drive.
           Until a command request a hard drive ressource, it does not touch it.
        2. Keeps an up-to-date, pickled version of the repository, to speed up things
           when they are a lot of files. Update are also done only when required.
           Changes are detected using data modification timestamps.

        For the moment, only (1) is implemented.
    """
    def __init__(self, directory, create=False):
        self.directory = directory
        self._databroker = None
        self._metacache = None
        self._metacache_modified = False # if True, cache will need to be written to disk.
        self._bibcache = None
        self._bibcache_modified = False # if True, cache will need to be written to disk.
        # does the filesystem supports subsecond stat time?
        self.nsec_support = os.stat('.').st_mtime != int(os.stat('.').st_mtime)
        if create:
            self._create()

    def close(self):
        self.flush_cache()

    @property
    def databroker(self):
        if self._databroker is None:
            self._databroker = databroker.DataBroker(self.directory, create=False)
        return self._databroker

    def _create(self):
        self._databroker = databroker.DataBroker(self.directory, create=True)

    @property
    def metacache(self):
        if self._metacache is None:
            try:
                self._metacache = self.databroker.pull_cache('metacache')
            except Exception as e: # take no prisonners; if something is wrong, no cache.
                self._metacache = {}
        return self._metacache

    @property
    def bibcache(self):
        if self._bibcache is None:
            try:
                self._bibcache = self.databroker.pull_cache('bibcache')
            except Exception as e:
                self._bibcache = {}
        return self._bibcache

    def flush_cache(self, force=False):
        """Write cache to disk"""
        if force or self._metacache_modified:
            self.databroker.push_cache('metacache', self.metacache)
            self._metacache_modified = False
        if force or self._bibcache_modified:
            self.databroker.push_cache('bibcache', self.bibcache)
            self._bibcache_modified = False

    def pull_metadata(self, citekey):
        mtime = self.databroker.filebroker.mtime_metafile(citekey)
        if citekey in self.metacache:
            cached_metadata = self.metacache[citekey]
            boundary = mtime if self.nsec_support else mtime + 1
            if cached_metadata.timestamp >= boundary:
                return cached_metadata.data

        # if we get here, we must update the cache.
        t = time.time()
        data = self.databroker.pull_metadata(citekey)
        self.metacache[citekey] = CacheEntry(data, t)
        self._metacache_modified = True
        return self.metacache[citekey].data

    def pull_bibentry(self, citekey):
        mtime = self.databroker.filebroker.mtime_bibfile(citekey)
        if citekey in self.bibcache:
            cached_bibdata = self.bibcache[citekey]
            boundary = mtime if self.nsec_support else mtime + 1
            if cached_bibdata.timestamp >= boundary:
                return cached_bibdata.data

        # if we get here, we must update the cache.
        t = time.time()
        data = self.databroker.pull_bibentry(citekey)
        self.bibcache[citekey] = CacheEntry(data, t)
        self._bibcache_modified = True
        return self.bibcache[citekey].data

    def push_metadata(self, citekey, metadata):
        self.databroker.push_metadata(citekey, metadata)
        mtime = self.databroker.filebroker.mtime_metafile(citekey)
        #print('push', mtime, metadata)
        self.metacache[citekey] = CacheEntry(metadata, mtime)
        self._metacache_modified = True

    def push_bibentry(self, citekey, bibdata):
        self.databroker.push_bibentry(citekey, bibdata)
        mtime = self.databroker.filebroker.mtime_bibfile(citekey)
        self.bibcache[citekey] = CacheEntry(bibdata, mtime)
        self._bibcache_modified = True

    def push(self, citekey, metadata, bibdata):
        self.databroker.push(citekey, metadata, bibdata)
        mtime = self.databroker.filebroker.mtime_metafile(citekey)
        self.metacache[citekey] = CacheEntry(metadata, mtime)
        self._metacache_modified = True
        mtime = self.databroker.filebroker.mtime_bibfile(citekey)
        self.bibcache[citekey] = CacheEntry(bibdata, mtime)
        self._bibcache_modified = True

    def remove(self, citekey):
        self.databroker.remove(citekey)
        if citekey in self.metacache:
            self.metacache.pop(citekey)
            self._metacache_modified = True
        if citekey in self.bibcache:
            self.bibcache.pop(citekey)
            self._bibcache_modified = True

    def exists(self, citekey, meta_check=False):
        return self.databroker.exists(citekey, meta_check=meta_check)

    def citekeys(self):
        return self.databroker.citekeys()

    def listing(self, filestats=True):
        return self.databroker.listing(filestats=filestats)

    def verify(self, bibdata_raw):
        return self.databroker.verify(bibdata_raw)

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

    def real_notepath(self, citekey):
        return self.databroker.real_notepath(citekey)

    def remove_note(self, citekey, silent=True):
        return self.databroker.remove_note(citekey, silent=True)

    def rename_note(self, old_citekey, new_citekey):
        return self.databroker.rename_note(old_citekey, new_citekey)
