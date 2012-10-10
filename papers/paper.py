import files
import color

class Paper(object):
    """Paper class. The object is responsible for the integrity of its own data,
    and for loading and writing it to disc.
    """

    @classmethod
    def from_disc(cls, name):
        p = Paper(name)
        self.bib_data = files.load_bibdata(self.name)
        self.metadata = files.load_meta(self.name)
        self.citekey  = self.metadata.get('metadata', 'citekey')
        self.number   = self.metadata.get('metadata', 'number')
        return p

    def __init__(self, name):
        self.name = name
        
        
        

