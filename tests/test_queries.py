import unittest

import dotdot
from pubs.query import (AuthorFilter, FieldFilter, YearFilter,
                        _query_block_to_filter, get_paper_filter,
                        InvalidQuery)

from pubs.paper import Paper

import fixtures

doe_paper    = Paper.from_bibentry(fixtures.doe_bibentry)
page_paper   = Paper.from_bibentry(fixtures.page_bibentry)
turing_paper = Paper.from_bibentry(fixtures.turing_bibentry,
                                   metadata=fixtures.turing_metadata)


class TestAuthorFilter(unittest.TestCase):

    def test_fails_if_no_author(self):
        no_doe = doe_paper.deepcopy()
        no_doe.bibentry['Doe2013']['author'] = []
        self.assertFalse(AuthorFilter('whatever')(no_doe))

    def test_match_case(self):
        self.assertTrue(AuthorFilter('doe')(doe_paper))
        self.assertTrue(AuthorFilter('doe', case_sensitive=False)(doe_paper))
        self.assertTrue(AuthorFilter('Doe')(doe_paper))

    def test_do_not_match_case(self):
        self.assertFalse(AuthorFilter('dOe')(doe_paper))
        self.assertFalse(AuthorFilter('dOe', case_sensitive=True)(doe_paper))
        self.assertFalse(AuthorFilter('doe', case_sensitive=True)(doe_paper))
        self.assertTrue(AuthorFilter('dOe', case_sensitive=False)(doe_paper))

    def test_match_not_first_author(self):
        self.assertTrue(AuthorFilter('motwani')(page_paper))

    def test_do_not_match_first_name(self):
        self.assertFalse(AuthorFilter('lawrence')(page_paper))


class TestCheckTag(unittest.TestCase):
    pass


class TestCheckYear(unittest.TestCase):

    def test_single_year(self):
        self.assertTrue(YearFilter('2013')(doe_paper))
        self.assertFalse(YearFilter('2014')(doe_paper))

    def test_before_year(self):
        self.assertTrue(YearFilter('-2013')(doe_paper))
        self.assertTrue(YearFilter('-2014')(doe_paper))
        self.assertFalse(YearFilter('-2012')(doe_paper))

    def test_after_year(self):
        self.assertTrue(YearFilter('2013-')(doe_paper))
        self.assertTrue(YearFilter('2012-')(doe_paper))
        self.assertFalse(YearFilter('2014-')(doe_paper))

    def test_year_range(self):
        self.assertTrue(YearFilter('')(doe_paper))
        self.assertTrue(YearFilter('-')(doe_paper))
        self.assertTrue(YearFilter('2013-2013')(doe_paper))
        self.assertTrue(YearFilter('2012-2014')(doe_paper))
        self.assertFalse(YearFilter('2014-2015')(doe_paper))
        with self.assertRaises(ValueError):
            YearFilter('2015-2014')(doe_paper)


class TestCheckField(unittest.TestCase):

    def test_match_case(self):
        self.assertTrue(FieldFilter('title', 'nice')(doe_paper))
        self.assertTrue(
            FieldFilter('title', 'nice', case_sensitive=False)(doe_paper))
        self.assertTrue(FieldFilter('year', '2013')(doe_paper))

    def test_do_not_match_case(self):
        self.assertTrue(
            FieldFilter('title', 'Title', case_sensitive=True)(doe_paper))
        self.assertFalse(
            FieldFilter('title', 'nice', case_sensitive=True)(doe_paper))


class TestCheckQueryBlock(unittest.TestCase):

    def test_raise_invalid_if_no_value(self):
        with self.assertRaises(InvalidQuery):
            _query_block_to_filter('title')

    def test_raise_invalid_if_too_much(self):
        with self.assertRaises(InvalidQuery):
            _query_block_to_filter('whatever:value:too_much')


class TestFilterPaper(unittest.TestCase):

    def test_case(self):
        self.assertTrue(get_paper_filter(['title:nice'])(doe_paper))
        self.assertTrue(get_paper_filter(['title:Nice'])(doe_paper))
        self.assertFalse(get_paper_filter(['title:nIce'])(doe_paper))

    def test_fields(self):
        self.assertTrue(get_paper_filter(['year:2013'])(doe_paper))
        self.assertTrue(get_paper_filter(['year:2010-'])(doe_paper))
        self.assertFalse(get_paper_filter(['year:2014'])(doe_paper))
        self.assertTrue(get_paper_filter(['author:doe'])(doe_paper))
        self.assertTrue(get_paper_filter(['author:Doe'])(doe_paper))

    def test_tags(self):
        self.assertTrue(get_paper_filter(['tag:computer'])(turing_paper))
        self.assertFalse(get_paper_filter(['tag:Ai'])(turing_paper))
        self.assertTrue(get_paper_filter(['tag:AI'])(turing_paper))
        self.assertTrue(get_paper_filter(['tag:ai'])(turing_paper))

    def test_multiple(self):
        self.assertTrue(get_paper_filter(['author:doe', 'year:2013'])(doe_paper))
        self.assertTrue(get_paper_filter(['author:doe', 'year:2010-2014'])(doe_paper))
        self.assertFalse(get_paper_filter(['author:doe', 'year:2014-'])(doe_paper))
        self.assertFalse(get_paper_filter(['author:doee', 'year:2014'])(doe_paper))


if __name__ == '__main__':
    unittest.main()
