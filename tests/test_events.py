from unittest import TestCase

from papers.events import Event


_output = None


class TestEvent(Event):
    def __init__(self, string):
        self.string = string

    def print_one(self):
        _output.append('one')


class AddEvent(Event):
    def __init__(self):
        pass

    def add(self, a, b):
        return a + b


@TestEvent.listen(12, 15)
def display(TestEventInstance, nb1, nb2):
    _output.append("%s %s %s"
                    % (TestEventInstance.string, nb1, nb2))


@TestEvent.listen()
def hello_word(TestEventInstance):
    _output.append('Helloword')


@TestEvent.listen()
def print_it(TestEventInstance):
    TestEventInstance.print_one()


@AddEvent.listen()
def do_it(AddEventInstance):
    _output.append(AddEventInstance.add(17, 25))


class TestEvents(TestCase):

    def setUp(self):
        global _output
        _output = []

    def test_listen_TestEvent(self):
        # using the callback system
        myevent = TestEvent('abcdefghijklmnopqrstuvwxyz')
        myevent.send()  # this one call three function
        correct = ['abcdefghijklmnopqrstuvwxyz 12 15',
                   'Helloword',
                   'one']
        self.assertEquals(_output, correct)

    def test_listen_AddEvent(self):
        addevent = AddEvent()
        addevent.send()
        correct = [42]
        self.assertEquals(_output, correct)
