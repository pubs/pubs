import os
import ConfigParser


MAIN_SECTION = 'papers'
CONFIG_PATH = os.path.expanduser('~/.papersrc')
DEFAULT_PAPERS_DIRECTORY = os.path.expanduser('~/.papers')
DEFAULT_OPEN_CMD = 'open'
try:
    DEFAULT_EDIT_CMD = os.environ['EDITOR']
except KeyError:
    DEFAULT_EDIT_CMD = 'vi'

DEFAULT_IMPORT_COPY = 'yes'
DEFAULT_IMPORT_MOVE = 'no'
DEFAULT_COLOR = 'yes'
DEFAULT_PLUGINS = 'texnote'

CONFIG = ConfigParser.SafeConfigParser({
    'papers-directory': DEFAULT_PAPERS_DIRECTORY,
    'open-cmd': DEFAULT_OPEN_CMD,
    'edit-cmd': DEFAULT_EDIT_CMD,
    'import-copy': DEFAULT_IMPORT_COPY,
    'import-move': DEFAULT_IMPORT_MOVE,
    'color': DEFAULT_COLOR,
    'plugins': DEFAULT_PLUGINS})
CONFIG.add_section(MAIN_SECTION)


def read_config():
    CONFIG.read(CONFIG_PATH)
    return CONFIG


def add_and_write_option(section, option, value):
    cfg = ConfigParser.ConfigParser()
    cfg.read(CONFIG_PATH)
    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, option, value)

    f = open(CONFIG_PATH, 'w')
    cfg.write(f)
    f.close()


def get_plugins(cfg):
    return cfg.get(MAIN_SECTION, 'plugins').split()


def get_boolean(value, default = False):
    value = str(value).lower()
    if value in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return default
