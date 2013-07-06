_listener = []


class Event(object):
    """Base event that can be sent to listeners.
    """

    def send(self):
        """ This function sends the instance of the class, i.e. the event
        to be sent, to all function that listen to it.
        """
        for cls, f, args in _listener:
            if isinstance(self, cls):
                f(self, *args)

    @classmethod
    def listen(cls, *args):
        def wrap(f):
            _listener.append((cls, f, args))

            # next step allow us to call the function itself without Event raised
            def wrapped_f(*args):
                f(*args)
            return wrapped_f
        return wrap


class RemoveEvent(Event):
    def __init__(self, citekey):
        self.citekey = citekey


class RenameEvent(Event):
    def __init__(self, paper, old_citekey):
        self.paper = paper
        self.old_citekey = old_citekey


class AddEvent(Event):
    def __init__(self, citekey):
        self.citekey = citekey
