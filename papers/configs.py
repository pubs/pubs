import os
import ConfigParser


DEFAULT_PAPERS_DIRECTORY = os.path.expanduser('~/.papers')
DEFAULT_OPEN_CMD = 'open'
try:
    DEFAULT_EDIT_CMD = os.environ['EDITOR']
except KeyError:
    DEFAULT_EDIT_CMD = 'vi'

DEFAULT_IMPORT_COPY = 'yes'
DEFAULT_IMPORT_MOVE = 'no'
DEFAULT_COLOR = 'yes'


CONFIG = ConfigParser.SafeConfigParser({
    'papers-directory': DEFAULT_PAPERS_DIRECTORY,
    'open-cmd': DEFAULT_OPEN_CMD,
    'edit-cmd': DEFAULT_EDIT_CMD,
    'import-copy': DEFAULT_IMPORT_COPY,
    'import-move': DEFAULT_IMPORT_MOVE,
    'color': DEFAULT_COLOR,
    })
CONFIG.add_section('papers')


def read_config():
    CONFIG.read(os.path.expanduser('~/.papersrc'))
    return CONFIG


def get_boolean(value, default):
    value = str(value).lower()
    if value in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return 0
