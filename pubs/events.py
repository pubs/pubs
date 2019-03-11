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


class PaperEvent(Event):
    _format = "Unknown modification of paper {citekey}."

    def __init__(self, citekey):
        self.citekey = citekey

    @property
    def description(self):
        return self._format.format(citekey=self.citekey)


class AddEvent(PaperEvent):
    _format = "Adds paper {citekey}."


class DocAddEvent(PaperEvent):
    _format = "Adds document {citekey}."


class RemoveEvent(PaperEvent):
    _format = "Removes paper {citekey}."


class DocRemoveEvent(PaperEvent):
    _format = "Removes document {citekey}."


class ModifyEvent(PaperEvent):
    _format = "Modifies paper {citekey}."


class RenameEvent(PaperEvent):
    _format = "Renames paper {old_citekey} to {citekey}."

    def __init__(self, paper, old_citekey):
        super(RenameEvent, self).__init__(paper.citekey)
        self.paper = paper
        self.old_citekey = old_citekey

    @property
    def description(self):
        return self._format.format(citekey=self.citekey, old_citekey=self.old_citekey)

class NoteEvent(PaperEvent):
    _format = "Modifies note {citekey}"
