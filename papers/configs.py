import os
import copy
from p3 import configparser

# constant stuff (DFT = DEFAULT)

MAIN_SECTION    = 'papers'
DFT_CONFIG_PATH = os.path.expanduser('~/.papersrc')
DFT_PAPERS_DIR  = os.path.expanduser('~/.papers')
DFT_OPEN_CMD    = 'open'
try:
    DFT_EDIT_CMD = os.environ['EDITOR']
except KeyError:
    DFT_EDIT_CMD = 'vi'

DFT_IMPORT_COPY = 'yes'
DFT_IMPORT_MOVE = 'no'
DFT_COLOR       = 'yes'
DFT_PLUGINS     = 'texnote'

DFT_CONFIG = {'papers_dir'  : DFT_PAPERS_DIR,
              'open_cmd'    : DFT_OPEN_CMD,
              'edit_cmd'    : DFT_EDIT_CMD,
              'import_copy' : DFT_IMPORT_COPY,
              'import_move' : DFT_IMPORT_MOVE,
              'color'       : DFT_COLOR,
              'plugins'     : DFT_PLUGINS
             }

BOOLEANS = {'import-copy', 'import-move', 'color'}


# package-shared config that can be accessed using :
# from configs import config
_config = None
def config(section = MAIN_SECTION):
    if config is None:
        raise ValueError, 'not config instanciated yet'
    _config._section = section
    return _config

class Config(object):

    def __init__(self):
        object.__setattr__(self, '_cfg', configparser.SafeConfigParser(DFT_CONFIG))
        object.__setattr__(self, '_section', MAIN_SECTION) # active section
        self._cfg.add_section(self._section)

    def as_global(self):
        global _config
        _config = self

    def load(self, path = DFT_CONFIG_PATH):
        self._cfg.read(path)
        return self

    def save(self, path = DFT_CONFIG_PATH):
        with open(path, 'w') as f:
            self._cfg.write(f)

    def __setattr__(self, name, value):
        if name in ('_cfg', '_section'):
            object.__setattr__(self, name, value)
        else:
            if type(value) is bool:
                BOOLEANS.add(name)
            self._cfg.set(self._section, name, str(value))

    def __getattr__(self, name):
        value = self._cfg.get(self._section, name)
        if name in BOOLEANS:
            value = str2bool(value)
        return value

    def items(self):
        for name, value in self._cfg.items(self._section):
            if name in BOOLEANS:
                value = str2bool(value)
            yield name, value

def str2bool(s):
    return str(s).lower() in ('yes', 'true', 't', 'y', '1')
