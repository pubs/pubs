from __future__ import unicode_literals

from . import filebroker
from . import endecoder
from .p3 import pickle
from . import __version__


class DataBroker(object):
    """ DataBroker class

        This is aimed at being a simple, high level interface to the content stored on disk.
        Requests are optimistically made, and exceptions are raised if something goes wrong.
    """

    def __init__(self, pubsdir, docsdir, create=False):
        self.filebroker = filebroker.FileBroker(pubsdir, create=create)
        self.endecoder  = endecoder.EnDecoder()
        self.docbroker  = filebroker.DocBroker(docsdir, scheme='docsdir', subdir='')
        self.notebroker = filebroker.DocBroker(pubsdir, scheme='notesdir', subdir='notes')

    # cache

    def close(self):
        pass

    def pull_cache(self, name):
        """Load cache data from disk. Exceptions are handled by the caller."""
        data_raw = self.filebroker.pull_cachefile(name)
        cache = pickle.loads(data_raw)
        if cache['version'] != __version__:
            raise ValueError('Cache not matching code version.')
        return cache['data']

    def push_cache(self, name, data):
        cache_content = {'version': __version__, 'data': data}
        data_raw = pickle.dumps(cache_content)
        self.filebroker.push_cachefile(name, data_raw)

    # filebroker+endecoder

    def pull_metadata(self, citekey):
        metadata_raw = self.filebroker.pull_metafile(citekey)
        return self.endecoder.decode_metadata(metadata_raw)

    def pull_bibentry(self, citekey):
        bibdata_raw = self.filebroker.pull_bibfile(citekey)
        try:
            return self.endecoder.decode_bibdata(bibdata_raw)
        except self.endecoder.BibDecodingError as e:
            # QUESTION: do we really want to obscure a more precise error message here?
            e.args = "Unable to decode bibtex for paper {}.".format(citekey)
            raise e

    def push_metadata(self, citekey, metadata):
        metadata_raw = self.endecoder.encode_metadata(metadata)
        self.filebroker.push_metafile(citekey, metadata_raw)

    def push_bibentry(self, citekey, bibdata):
        bibdata_raw = self.endecoder.encode_bibdata(bibdata)
        self.filebroker.push_bibfile(citekey, bibdata_raw)

    def push(self, citekey, metadata, bibdata):
        self.filebroker.push(citekey, metadata, bibdata)

    def remove(self, citekey):
        self.filebroker.remove(citekey)

    def exists(self, citekey, meta_check=False):
        """ Checks wether the bibtex of a citekey exists.

            :param meta_check:  if True, will return if both the bibtex and the meta file exists.
        """
        return self.filebroker.exists(citekey, meta_check=meta_check)

    def citekeys(self):
        listings = self.listing(filestats=False)
        return set(listings['bibfiles'])

    def listing(self, filestats=True):
        return self.filebroker.listing(filestats=filestats)

    # docbroker

    def in_docsdir(self, docpath):
        return self.docbroker.in_docsdir(docpath)

    def real_docpath(self, docpath):
        return self.docbroker.real_docpath(docpath)

    def add_doc(self, citekey, source_path, overwrite=False):
        return self.docbroker.add_doc(citekey, source_path, overwrite=overwrite)

    def remove_doc(self, docpath, silent=True):
        return self.docbroker.remove_doc(docpath, silent=silent)

    def rename_doc(self, docpath, new_citekey):
        return self.docbroker.rename_doc(docpath, new_citekey)

    # notesbroker

    def _notepath(self, citekey, extension):
        return 'notesdir://{}.{}'.format(citekey, extension)

    def real_notepath(self, citekey, extension):
        return self.notebroker.real_docpath(self._notepath(citekey, extension))

    def remove_note(self, citekey, extension, silent=True):
        return self.notebroker.remove_doc(self._notepath(citekey, extension),
                                          silent=silent)

    def rename_note(self, old_citekey, new_citekey, extension):
        return self.notebroker.rename_doc(
            self._notepath(old_citekey, extension), new_citekey)
