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

def get_pubspath(verify=True):
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

def load_conf(check_conf=True):
    """Load the user config"""
    pubspath = get_pubspath(verify=True)
    with open(pubspath, 'r') as f:
        conf = configobj.ConfigObj(f.readlines(), configspec=configspec)

    if check_conf:
        validator = validate.Validator()
        results   = conf.validate(validator, copy=True)
        assert results == True, '{}'.format(results) # TODO: precise error dialog when parsing error

    return conf

def save_conf(conf):
    with open(get_pubspath(verify=False), 'w') as f:
        conf.write(outfile=f)
