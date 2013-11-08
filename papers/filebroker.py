import os

def check_file(path, fail=True):
    if fail:
        if not os.path.exists(path):
            raise IOError("File does not exist: {}.".format(path))
        if not os.path.isfile(path):
            raise IOError("{} is not a file.".format(path))
        return True
    else:
        return os.path.exists(path) and os.path.isfile(path)

def check_directory(path, fail=True):
    if fail:
        if not os.path.exists(path):
            raise IOError("File does not exist: {}.".format(path))
        if not os.path.isdir(path):
            raise IOError("{} is not a directory.".format(path))
        return True
    else:
        return os.path.exists(path) and os.path.isdir(path)

def read_file(filepath):
    check_file(filepath)
    with open(filepath, 'r') as f:
        s = f.read()
    return s
        
def write_file(filepath, data):
    check_directory(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        f.write(data)


class FileBroker(object):
    """ Handles all access to meta and bib files of the repository.

        * Does *absolutely no* encoding/decoding.
        * Communicate failure with exceptions.
    """

    def __init__(self, directory, create=False):
        self.directory = directory        
        self.metadir = os.path.join(self.directory, 'meta')
        self.bibdir  = os.path.join(self.directory, 'bib')
        if create:
            self._create()
        check_directory(self.directory)
        check_directory(self.metadir)
        check_directory(self.bibdir)
                
    def _create(self):
        if not check_directory(self.directory, fail = False):
            os.mkdir(self.directory)
        if not check_directory(self.metadir, fail = False):
            os.mkdir(self.metadir)
        if not check_directory(self.bibdir, fail = False):
            os.mkdir(self.bibdir)
    
    def pull_metafile(self, citekey):
        filepath = os.path.join(self.metadir, citekey + '.yaml')
        return read_file(filepath)

    def pull_bibfile(self, citekey):
        filepath = os.path.join(self.bibdir, citekey + '.bibyaml')
        return read_file(filepath)
        
    def push_metafile(self, citekey, metadata):
        filepath = os.path.join(self.metadir, citekey + '.yaml')
        write_file(filepath, metadata)
    
    def push_bibfile(self, citekey, bibdata):
        filepath = os.path.join(self.bibdir, citekey + '.bibyaml')
        write_file(filepath, bibdata)
        
    def push(self, citekey, metadata, bibdata):
        self.push_metafile(citekey, metadata)
        self.push_bibfile(citekey, bibdata)

    def remove(self, citekey):
        metafilepath = os.path.join(self.metadir, citekey + '.yaml')
        os.remove(metafilepath)
        bibfilepath = os.path.join(self.bibdir, citekey + '.bibyaml')
        os.remove(bibfilepath)

    def listing(self, filestats = True):
        metafiles = []
        for filename in os.listdir(self.metadir):
            stats = os.stat(os.path.join(path, f))
            metafiles.append(filename, stats)

        bibfiles = []
        for filename in os.listdir(self.bibdir):
            stats = os.stat(os.path.join(path, f))
            bibfiles.append(filename, stats)

        return {'metafiles': metafiles, 'bibfiles': bibfiles}

