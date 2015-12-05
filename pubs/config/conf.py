import os

import configobj
import validate

from .spec import configspec


DFT_CONFIG_PATH = os.path.expanduser('~/.pubsrc')

def load_default_conf():
    """Loads the default configuration"""
    default_conf = configobj.ConfigObj(configspec=configspec)
    validator = validate.Validator()
    default_conf.validate(validator, copy=True)
    return default_conf

def get_confpath(verify=True):
    """Returns the pubs path.
    If verify is True, verify that pubs.conf exist in the directory,
    and exit with an error if not.
    """
    confpath = DFT_CONFIG_PATH
    if 'PUBSCONF' in os.environ:
        confpath = os.path.abspath(os.path.expanduser(os.environ['PUBSCONF']))
    if verify:
        if not os.path.isfile(confpath):
            from .. import uis
            ui = uis.get_ui()
            ui.error('configuration file not found at `{}`'.format(confpath))
            ui.exit(error_code=1)
    return confpath

def check_conf(conf):
    """Type checks a configuration"""
    validator = validate.Validator()
    results   = conf.validate(validator, copy=True)
    assert results == True, '{}'.format(results) # TODO: precise error dialog when parsing error

def load_conf(check=True, path=None):
    """Load the user config"""
    if path is None:
        path = get_confpath(verify=True)
    with open(path, 'rb') as f:
        conf = configobj.ConfigObj(f.readlines(), configspec=configspec)

    if check:
        check_conf(conf)

    return conf

def save_conf(conf, path=None):
    if path is None:
        path = get_confpath(verify=False)
    with open(path, 'wb') as f:
        conf.write(outfile=f)
