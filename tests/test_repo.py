import unittest

from papers.repo import Repository, _str_incr, _to_suffix


class TestCitekeyGeneration(unittest.TestCase):

    def test_string_increment(self):
        l = []
        self.assertEqual(_to_suffix(l), '')
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'a')
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'b')
        l = ['z']
        _str_incr(l)
        self.assertEqual(_to_suffix(l), 'aa')

    def test_generated_key_is_unique(self):
        pass
