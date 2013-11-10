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
        self.docbroker  = filebroker.DocBroker(directory) 

    # filebroker+endecoder

    def pull_metadata(self, citekey):
        metadata_raw = self.filebroker.pull_metafile(citekey)
        return self.endecoder.decode_metadata(metadata_raw)
        
    def pull_bibdata(self, citekey):
        bibdata_raw = self.filebroker.pull_bibfile(citekey)
        return self.endecoder.decode_bibdata(bibdata_raw)
        
    def push_metadata(self, citekey, metadata):
        metadata_raw = self.endecoder.encode_metadata(metadata)
        self.filebroker.push_metafile(citekey, metadata_raw)
    
    def push_bibdata(self, citekey, bibdata):
        bibdata_raw = self.endecoder.encode_bibdata(bibdata)
        self.filebroker.push_bibfile(citekey, bibdata_raw)
        
    def push(self, citekey, metadata, bibdata):
        self.filebroker.push(citekey, metadata, bibdata)

    def remove(self, citekey):
        self.filebroker.remove(citekey)

    def exists(self, citekey, both = True):
        return self.filebroker.exists(citekey, both=both)
        
    def listing(self, filestats=True):
        return self.filebroker.listing(filestats=filestats)

    def verify(self, bibdata_raw):
        try:
            return self.endecoder.decode_bibdata(bibdata_raw)
        except ValueError:
            return None

    # docbroker

    def is_pubsdir_doc(self, docpath):
        return self.docbroker.is_pubsdir_doc(docpath)

    def copy_doc(self, citekey, source_path, overwrite=False):
        return self.docbroker.copy_doc(citekey, source_path, overwrite=overwrite)

    def remove_doc(self, docpath, silent=True):
        return self.docbroker.remove_doc(docpath, silent=silent)

    def real_docpath(self, docpath):
        return self.docbroker.real_docpath(docpath)        