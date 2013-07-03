_listener = {}


class Event(object):
    """Base event that can be sent to listeners.
    """

    def send(self):
        """ This function sends the instance of the class, i.e. the event
        to be sent, to all function that listen to it.
        """
        if self.__class__ in _listener:
            for f, args in _listener[self.__class__]:
                f(self, *args)

    @classmethod
    def listen(cls, *args):
        def wrap(f):
            if cls not in _listener:
                _listener[cls] = []
            _listener[cls].append((f, args))

            # next step allow us to call the function itself without Event raised
            def wrapped_f(*args):
                f(*args)
            return wrapped_f
        return wrap


class RemoveEvent(Event):
    def __init__(self, ui, citekey):
        self.ui = ui
        self.citekey = citekey
