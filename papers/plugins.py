import importlib
from .configs import config

PLUGIN_NAMESPACE = 'plugs'

_classes = []
_instances = {}


class PapersPlugin(object):
    """The base class for all plugins. Plugins provide
    functionality by defining a subclass of PapersPlugin and overriding
    the abstract methods defined here.
    """
    def __init__(self):
        """Perform one-time plugin setup.
        """
        self.name = self.__module__.split('.')[-1]

    #ui and given again to stay consistent with the core papers cmd.
    #two options:
    #- create specific cases in script papers/papers
    #- do not store self.ui and use them if needed when command is called
    #this may end up with a lot of function with config/ui in argument
    #or just keep it that way...
    def parser(self, subparsers):
        """ Should return the parser with plugins specific command.
        This is a basic example
        """
        parser = subparsers.add_parser(self.name, help="echo string in argument")
        parser.add_argument('strings', nargs='*', help='the strings')
        return parser

    def command(self, args):
        """This function will be called with argument defined in the parser above
        This is a basic example
        """

        ui = args.ui
        strings = args.strings

        for s in strings:
            print(s)

    @classmethod
    def get_instance(cls):
        if cls in _instances:
            return _instances[cls]
        else:
            raise RuntimeError("{} instance not created".format(cls.__name__))


def load_plugins(ui, names):
    """Imports the modules for a sequence of plugin names. Each name
    must be the name of a Python module under the "PLUGIN_NAMESPACE" namespace
    package in sys.path; the module indicated should contain the
    PapersPlugin subclasses desired.
    """
    for name in names:
        modname = '%s.%s.%s.%s' % ('papers', PLUGIN_NAMESPACE, name, name)
        #try:
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
                    _instances[obj] = obj()

        #except:
        #    ui.warning('error loading plugin {}'.format(name))


def get_plugins():
    return _instances
