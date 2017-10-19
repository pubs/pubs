import os
import platform

import configobj
import validate

from .spec import configspec


DFT_CONFIG_PATH = os.path.expanduser('~/.pubsrc')


class ConfigurationNotFound(IOError):

    def __init__(self, path):
        super(ConfigurationNotFound, self).__init__(
            "No configuration found at path {}. Maybe you need to initialize "
            "your repository with `pubs init` or specify a --config argument."
            "".format(path))


def post_process_conf(conf):
    """Do some post processing on the configuration"""
    check_conf(conf)
    if conf['main']['docsdir'] == 'docsdir://':
        conf['main']['docsdir'] = os.path.join(conf['main']['pubsdir'], 'doc')
    return conf


def load_default_conf():
    """Load the default configuration"""
    default_conf = configobj.ConfigObj(configspec=configspec)
    default_conf = post_process_conf(default_conf)
    return default_conf


def get_confpath(verify=True):
    """Return the configuration filepath
    If verify is True, verify that the file exists and exit with an error if not.
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
    """Type check a configuration"""
    validator = validate.Validator()
    results = conf.validate(validator, copy=True)
    assert (results is True), '{}'.format(results)  # TODO: precise error dialog when parsing error


def load_conf(path=None):
    """Load the configuration"""
    if path is None:
        path = get_confpath(verify=True)
    if not os.path.exists(path):
        raise ConfigurationNotFound(path)
    conf = configobj.ConfigObj(path, configspec=configspec)
    conf.filename = path
    conf = post_process_conf(conf)
    return conf


def save_conf(conf, path=None):
    """Save the configuration."""
    if path is not None:
        conf.filename = path
    elif conf.filename is None:
        conf.filename = get_confpath(verify=False)
    with open(conf.filename, 'wb') as f:
        conf.write(outfile=f)


def default_open_cmd():
    """Chooses the default command to open documents"""
    if platform.system() == 'Darwin':
        return 'open'
    elif platform.system() == 'Linux':
        return 'xdg-open'
    elif platform.system() == 'Windows':
        return 'start'
    else:
        return None
