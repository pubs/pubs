import os
    
import files
import color
import pretty


class NoDocumentFile(Exception):
    pass


class Paper(object):
    """Paper class. The object is responsible for the integrity of its own data,
    and for loading and writing it to disc.
    """

    @classmethod
    def from_disc(cls, name, citekey = None, number = None):
        bib_data = files.load_bibdata(name)
        metadata = files.load_meta(name)
        p = Paper(name, bib_data = bib_data, metadata = metadata, 
                        citekey = citekey, number = number)
        return p

    @classmethod
    def from_bibpdffiles(cls, pdfpath, bibpath):
        bib_data = cls.import_bibdata(bibpath)
        name, meta = cls.create_meta(bib_data, pdfpath=pdfpath)
        p = Paper(name, bib_data = bib_data, metadata = meta)
        
        return p            

    def __init__(self, name, bib_data = None, metadata = None, 
                       citekey = None, number = None):
        self.name = name
        self.bib_data = bib_data
        self.metadata = metadata
        self.citekey  = citekey
        self.number   = number

    def has_file(self):
        """Whether there exist a document file for this entry.
        """
        return self.metadata['path'] is not None

    def get_file_path(self):
        if self.has_file():
            return self.metadata['path']
        else:
            raise NoDocumentFile

    def check_file(self):
        return files.check_file(self.get_file_path())
                
    def save_to_disc(self):
        files.save_bibdata(self.bib_data, self.name)
        files.save_meta(self.metadata, self.name)

    @classmethod
    def import_bibdata(cls, bibfile):        
        """Import bibligraphic data from a .bibyaml, .bib or .bibtex file"""
        fullbibpath = os.path.abspath(bibfile)
        
        bib_data = files.load_externalbibfile(fullbibpath)
        print('{}bibliographic data present in {}{}{}'.format(
               color.grey, color.cyan, bibfile, color.end))
        print(pretty.bib_desc(bib_data))
        
        return bib_data

    @classmethod
    def create_meta(cls, bib_data, pdfpath=None):
    
        if pdfpath is None:
            name = bib_data.entries.keys()[0]
            # TODO this introduces a bug and a security issue since the name
            # is used to generate a file name that is written. It should be
            # escaped here. (22/10/2012)
            fullpdfpath, ext = None, None
        else:
            fullpdfpath = os.path.abspath(pdfpath)
            files.check_file(fullpdfpath)
        
            name, ext = files.name_from_path(pdfpath)
    
        meta = {}
    
        meta['name'] = name
        meta['extension'] = ext
        meta['path'] = fullpdfpath
    
        meta['notes'] = []
        
        return name, meta
