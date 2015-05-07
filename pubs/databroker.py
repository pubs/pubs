from . import filebroker
from . import endecoder


class DataBroker(object):
    """ DataBroker class

        This is aimed at being a simple, high level interface to the content stored on disk.
        Requests are optimistically made, and exceptions are raised if something goes wrong.
    """

    def __init__(self, directory, create=False):
        self.filebroker = filebroker.FileBroker(directory, create=create)
        self.endecoder  = endecoder.EnDecoder()
        self.docbroker  = filebroker.DocBroker(directory, scheme='docsdir', subdir='doc')
        self.notebroker = filebroker.DocBroker(directory, scheme='notesdir', subdir='notes')

    # filebroker+endecoder

    def pull_metadata(self, citekey):
        metadata_raw = self.filebroker.pull_metafile(citekey)
        return self.endecoder.decode_metadata(metadata_raw)

    def pull_bibentry(self, citekey):
        bibdata_raw = self.filebroker.pull_bibfile(citekey)
        return self.endecoder.decode_bibdata(bibdata_raw)

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

    def verify(self, bibdata_raw):
        """Will return None if bibdata_raw can't be decoded"""
        try:
            return self.endecoder.decode_bibdata(bibdata_raw)
        except ValueError:
            return None

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

    def real_notepath(self, citekey):
        notepath = 'notesdir://{}.txt'.format(citekey)
        return self.notebroker.real_docpath(notepath)

    def remove_note(self, citekey, silent=True):
        notepath = 'notesdir://{}.txt'.format(citekey)
        return self.notebroker.remove_doc(notepath, silent=silent)

    def rename_note(self, old_citekey, new_citekey):
        notepath = 'notesdir://{}.txt'.format(old_citekey)
        return self.notebroker.rename_doc(notepath, new_citekey)

