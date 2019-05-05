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


    # Command events

class PreCommandEvent(Event):
    description = "Triggered before the command is executed"

class PostCommandEvent(Event):
    description = "Triggered after the command is executed"


    # Paper changes

class PaperChangeEvent(Event):
    _format = "Unspecified modification of paper {citekey}."

    def __init__(self, citekey):
        self.citekey = citekey

    @property
    def description(self):
        return self._format.format(citekey=self.citekey)

# Used by repo.push_paper()
class AddEvent(PaperChangeEvent):
    _format = "Adds paper {citekey}."

# Used by repo.push_doc()
class DocAddEvent(PaperChangeEvent):
    _format = "Adds document for {citekey}."

# Used by repo.remove_paper()
class RemoveEvent(PaperChangeEvent):
    _format = "Removes paper for {citekey}."

# Used by repo.remove_doc()
class DocRemoveEvent(PaperChangeEvent):
    _format = "Removes document for {citekey}."

# Used by commands.tag_cmd.command()
class TagEvent(PaperChangeEvent):
    _format = "Updates tags for {citekey}."

# Used by commands.edit_cmd.command()
class ModifyEvent(PaperChangeEvent):
    _format = "Modifies {file_type} file of {citekey}."

    def __init__(self, citekey, file_type):
        super(ModifyEvent, self).__init__(citekey)
        self.file_type = file_type

    @property
    def description(self):
        return self._format.format(citekey=self.citekey, file_type=self.file_type)

# Used by repo.rename_paper()
class RenameEvent(PaperChangeEvent):
    _format = "Renames paper {old_citekey} to {citekey}."

    def __init__(self, paper, old_citekey):
        super(RenameEvent, self).__init__(paper.citekey)
        self.paper = paper
        self.old_citekey = old_citekey

    @property
    def description(self):
        return self._format.format(citekey=self.citekey, old_citekey=self.old_citekey)

# Used by commands.note_cmd.command()
class NoteEvent(PaperChangeEvent):
    _format = "Modifies note {citekey}."
