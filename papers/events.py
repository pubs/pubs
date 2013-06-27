_listener = {}


class Event(object):
    def __init__(self, string):
        """This is an example of simple event that can be raised
        Inherit from this class and redefine whatever you need,
        except the send funtion
        """
        self.string = string

    def send(self):
        """ This function sends the instance of the class, i.e. the event
        to be sent, to all function that listen to it.
        """
        if self.__class__.__name__ in _listener:
            for f, args in _listener[self.__class__.__name__]:
                f(self, *args)

    @classmethod
    def listen(cls, *args):
        def wrap(f):
            if cls.__name__ not in _listener:
                _listener[cls.__name__] = []
            _listener[cls.__name__].append((f, args))

            # next step allow us to call the function itself without Event raised
            def wrapped_f(*args):
                f(*args)
            return wrapped_f
        return wrap


class RemoveEvent(Event):
    def __init__(self, config, ui, citekey):
        self.config = config
        self.ui = ui
        self.citekey = citekey


if __name__ == "__main__":

    class TestEvent(Event):
        def print_one(self):
            print 'one'

    @TestEvent.listen(12, 15)
    def Display(TestEventInstance, nb1, nb2):
        print TestEventInstance.string, nb1, nb2

    @TestEvent.listen()
    def Helloword(TestEventInstance):
        print 'Helloword'

    @TestEvent.listen()
    def PrintIt(TestEventInstance):
        TestEventInstance.print_one()

    class AddEvent(Event):
        def __init__(self):
            pass

        def add(self, a, b):
            return a + b

    @AddEvent.listen()
    def DoIt(AddEventInstance):
        print AddEventInstance.add(17, 25)

    # using the callback system
    myevent = TestEvent('abcdefghijklmnopqrstuvwxyz')
    myevent.send()  # this one call three function

    addevent = AddEvent()
    addevent.send()

    # but also work without the event raising system!
    Display(myevent, 12, 15)
    Helloword(myevent)
    PrintIt(myevent)
    DoIt(addevent)
