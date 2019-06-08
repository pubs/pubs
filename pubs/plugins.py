import importlib

PLUGIN_NAMESPACE = 'plugs'

_classes = []
_instances = {}


class PapersPlugin(object):
    """The base class for all plugins. Plugins provide
    functionality by defining a subclass of PapersPlugin and overriding
    the abstract methods defined here.
    """

    name = None

    def get_commands(self, subparsers, conf):
        """Populates the parser with plugins specific command.
        Returns iterable of pairs (command name, command function to call).
        """
        return []

    @classmethod
    def get_instance(cls):
        if cls in _instances:
            return _instances[cls]
        else:
            raise RuntimeError("{} instance not created".format(cls.__name__))

    @classmethod
    def is_loaded(cls):
        return cls in _instances


def load_plugins(conf, ui):
    """Imports the modules for a sequence of plugin names. Each name
    must be the name of a Python module under the "PLUGIN_NAMESPACE" namespace
    package in sys.path; the module indicated should contain the
    PapersPlugin subclasses desired.
    """
    global _classes, _instances
    _classes, _instances = [], {}
    for name in conf['plugins']['active']:
        if len(name) > 0:
            modname = '{}.{}.{}.{}'.format('pubs', PLUGIN_NAMESPACE, name, name)
            try:
                namespace = importlib.import_module(modname)
            except ImportError as exc:
                # Again, this is hacky:
                if exc.args[0].endswith(' ' + name):
                    ui.warning('plugin {} not found'.format(name))
                else:
                    raise
            else:
                for obj in namespace.__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, PapersPlugin) \
                            and obj != PapersPlugin:
                        _classes.append(obj)
                        _instances[obj] = obj(conf, ui)


def get_plugins():
    return _instances
