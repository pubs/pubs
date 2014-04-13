import unittest

import dotdot
from pubs.commands.list_cmd import (_check_author_match,
                                      _check_field_match,
                                      _check_query_block,
                                      filter_paper,
                                      InvalidQuery)

from pubs.paper import Paper

import fixtures

doe_paper    = Paper(fixtures.doe_bibdata)
page_paper   = Paper(fixtures.page_bibdata)
turing_paper = Paper(fixtures.turing_bibdata, metadata=fixtures.turing_metadata)

class TestAuthorFilter(unittest.TestCase):

    def test_fails_if_no_author(self):
        no_doe = doe_paper.deepcopy()
        no_doe.bibentry['author'] = []
        self.assertTrue(not _check_author_match(no_doe, 'whatever'))

    def test_match_case(self):
        self.assertTrue(_check_author_match(doe_paper, 'doe'))
        self.assertTrue(_check_author_match(doe_paper, 'doe',
                                            case_sensitive=False))

    def test_do_not_match_case(self):
        self.assertFalse(_check_author_match(doe_paper, 'dOe'))
        self.assertFalse(_check_author_match(doe_paper, 'doe',
                                             case_sensitive=True))

    def test_match_not_first_author(self):
        self.assertTrue(_check_author_match(page_paper, 'motwani'))

    def test_do_not_match_first_name(self):
        self.assertTrue(not _check_author_match(page_paper, 'larry'))


class TestCheckTag(unittest.TestCase):
    pass


class TestCheckField(unittest.TestCase):

    def test_match_case(self):
        self.assertTrue(_check_field_match(doe_paper, 'title', 'nice'))
        self.assertTrue(_check_field_match(doe_paper, 'title', 'nice',
                                           case_sensitive=False))
        self.assertTrue(_check_field_match(doe_paper, 'year', '2013'))

    def test_do_not_match_case(self):
        self.assertTrue(_check_field_match(doe_paper, 'title',
                                            'Title', case_sensitive=True))
        self.assertFalse(_check_field_match(doe_paper, 'title', 'nice',
                                             case_sensitive=True))


class TestCheckQueryBlock(unittest.TestCase):

    def test_raise_invalid_if_no_value(self):
        with self.assertRaises(InvalidQuery):
            _check_query_block(doe_paper, 'title')

    def test_raise_invalid_if_too_much(self):
        with self.assertRaises(InvalidQuery):
            _check_query_block(doe_paper, 'whatever:value:too_much')


class TestFilterPaper(unittest.TestCase):

    def test_case(self):
        self.assertTrue (filter_paper(doe_paper, ['title:nice']))
        self.assertTrue (filter_paper(doe_paper, ['title:Nice']))
        self.assertFalse(filter_paper(doe_paper, ['title:nIce']))

    def test_fields(self):
        self.assertTrue (filter_paper(doe_paper, ['year:2013']))
        self.assertFalse(filter_paper(doe_paper, ['year:2014']))
        self.assertTrue (filter_paper(doe_paper, ['author:doe']))
        self.assertTrue (filter_paper(doe_paper, ['author:Doe']))

    def test_tags(self):
        self.assertTrue (filter_paper(turing_paper, ['tag:computer']))
        self.assertFalse(filter_paper(turing_paper, ['tag:Ai']))
        self.assertTrue (filter_paper(turing_paper, ['tag:AI']))
        self.assertTrue (filter_paper(turing_paper, ['tag:ai']))

    def test_multiple(self):
        self.assertTrue (filter_paper(doe_paper,
                                     ['author:doe', 'year:2013']))
        self.assertFalse(filter_paper(doe_paper,
                                      ['author:doe', 'year:2014']))
        self.assertFalse(filter_paper(doe_paper,
                                      ['author:doee', 'year:2014']))


if __name__ == '__main__':
    unittest.main()
