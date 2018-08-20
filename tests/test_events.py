import unittest

import dotdot
from pubs.events import Event


_output = None


class StringEvent(Event):
    def __init__(self, string):
        self.string = string

    def print_one(self):
        _output.append('one')


class AddEvent(Event):
    def __init__(self):
        pass

    def add(self, a, b):
        return a + b


class Info(Event):
    def __init__(self, info):
        self.info = info


class SpecificInfo(Info):
    def __init__(self, info, specific):
        Info.__init__(self, info)
        self.specific = specific


@StringEvent.listen(12, 15)
def display(StringEventInstance, nb1, nb2):
    _output.append("%s %s %s"
                    % (StringEventInstance.string, nb1, nb2))


@StringEvent.listen()
def hello_word(StringEventInstance):
    _output.append('Helloword')


@StringEvent.listen()
def print_it(StringEventInstance):
    StringEventInstance.print_one()


@AddEvent.listen()
def do_it(AddEventInstance):
    _output.append(AddEventInstance.add(17, 25))


@Info.listen()
def collect_info_instance(infoevent):
    _output.append(infoevent.info)
    if isinstance(infoevent, SpecificInfo):
        _output.append(infoevent.specific)


class TestEvents(unittest.TestCase):

    def setUp(self):
        global _output
        _output = []

    def test_listen_StringEvent(self):
        # using the callback system
        myevent = StringEvent('abcdefghijklmnopqrstuvwxyz')
        myevent.send()  # this one call three function
        correct = ['abcdefghijklmnopqrstuvwxyz 12 15',
                   'Helloword',
                   'one']
        self.assertEqual(_output, correct)

    def test_listen_AddEvent(self):
        addevent = AddEvent()
        addevent.send()
        correct = [42]
        self.assertEqual(_output, correct)

    def test_listen_Info(self):
        Info('info').send()
        SpecificInfo('info', 'specific').send()
        correct = ['info', 'info', 'specific']
        self.assertEqual(_output, correct)


if __name__ == '__main__':
    unittest.main()
