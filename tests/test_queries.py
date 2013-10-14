from unittest import TestCase

import testenv
import fixtures
from papers.commands.list_cmd import (_check_author_match,
                                      _check_field_match,
                                      _check_query_block,
                                      filter_paper,
                                      InvalidQuery)


class TestAuthorFilter(TestCase):

    def test_fails_if_no_author(self):
        no_doe = fixtures.doe2013.copy()
        no_doe.bibentry.persons = {}
        self.assertTrue(not _check_author_match(no_doe, 'whatever'))

    def test_match_case(self):
        self.assertTrue(_check_author_match(fixtures.doe2013, 'doe'))
        self.assertTrue(_check_author_match(fixtures.doe2013, 'doe',
                                            case_sensitive=False))

    def test_do_not_match_case(self):
        self.assertFalse(_check_author_match(fixtures.doe2013, 'dOe'))
        self.assertFalse(_check_author_match(fixtures.doe2013, 'doe',
                                             case_sensitive=True))

    def test_match_not_first_author(self):
        self.assertTrue(_check_author_match(fixtures.page99, 'wani'))

    def test_do_not_match_first_name(self):
        self.assertTrue(not _check_author_match(fixtures.page99, 'larry'))


class TestCheckTag(TestCase):
    pass


class TestCheckField(TestCase):

    def test_match_case(self):
        self.assertTrue(_check_field_match(fixtures.doe2013, 'title', 'nice'))
        self.assertTrue(_check_field_match(fixtures.doe2013, 'title', 'nice',
                                           case_sensitive=False))
        self.assertTrue(_check_field_match(fixtures.doe2013, 'year', '2013'))

    def test_do_not_match_case(self):
        self.assertFalse(_check_field_match(fixtures.doe2013, 'title',
                                            'Title', case_sensitive=True))
        self.assertFalse(_check_field_match(fixtures.doe2013, 'title', 'nice',
                                             case_sensitive=True))


class TestCheckQueryBlock(TestCase):

    def test_raise_invalid_if_no_value(self):
        with self.assertRaises(InvalidQuery):
            _check_query_block(fixtures.doe2013, 'title')

    def test_raise_invalid_if_too_much(self):
        with self.assertRaises(InvalidQuery):
            _check_query_block(fixtures.doe2013, 'whatever:value:too_much')


class TestFilterPaper(TestCase):

    def test_case(self):
        self.assertTrue(filter_paper(fixtures.doe2013, ['title:nice']))
        self.assertTrue(filter_paper(fixtures.doe2013, ['title:Nice']))
        self.assertFalse(filter_paper(fixtures.doe2013, ['title:nIce']))

    def test_fields(self):
        self.assertTrue(filter_paper(fixtures.doe2013, ['year:2013']))
        self.assertFalse(filter_paper(fixtures.doe2013, ['year:2014']))
        self.assertTrue(filter_paper(fixtures.doe2013, ['author:doe']))
        self.assertTrue(filter_paper(fixtures.doe2013, ['author:Doe']))

    def test_tags(self):
        self.assertTrue(filter_paper(fixtures.turing1950, ['tag:computer']))
        self.assertFalse(filter_paper(fixtures.turing1950, ['tag:Ai']))
        self.assertTrue(filter_paper(fixtures.turing1950, ['tag:AI']))
        self.assertTrue(filter_paper(fixtures.turing1950, ['tag:ai']))

    def test_multiple(self):
        self.assertTrue(filter_paper(fixtures.doe2013,
                                     ['author:doe', 'year:2013']))
        self.assertFalse(filter_paper(fixtures.doe2013,
                                      ['author:doe', 'year:2014']))
        self.assertFalse(filter_paper(fixtures.doe2013,
                                      ['author:doee', 'year:2014']))
