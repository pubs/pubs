import unittest
from datetime import datetime

import dotdot
import fake_env
import fixtures

from pubs.repo import Repository, _base27, CiteKeyCollision, InvalidReference
from pubs.paper import Paper
from pubs import configs


class TestRepo(fake_env.TestFakeFs):

    def setUp(self):
        super(TestRepo, self).setUp()
        self.repo = Repository(configs.Config(), create=True)
        self.repo.push_paper(Paper.from_bibentry(fixtures.turing_bibentry))


class TestCitekeyGeneration(TestRepo):

    def test_string_increment(self):
        self.assertEqual(_base27(0), '')
        for i in range(26):
            self.assertEqual(_base27(i + 1), chr(97 + i))
            self.assertEqual(_base27(26 + i + 1), 'a' + chr(97 + i))

    def test_generated_key_is_unique(self):
        self.repo.push_paper(Paper.from_bibentry(fixtures.doe_bibentry))
        c = self.repo.unique_citekey('Doe2013')
        self.repo.push_paper(Paper.from_bibentry(fixtures.doe_bibentry,
                                                 citekey='Doe2013a'))
        c = self.repo.unique_citekey('Doe2013')
        self.assertEqual(c, 'Doe2013b')


class TestPushPaper(TestRepo):

    def test_raises_value_error_on_existing_key(self):
        with self.assertRaises(CiteKeyCollision):
            self.repo.push_paper(Paper.from_bibentry(fixtures.turing_bibentry))

    def test_pushes_paper_bibdata(self):
        orig = fixtures.doe_bibentry
        self.repo.push_paper(Paper.from_bibentry(orig))
        retrieved = self.repo.databroker.pull_bibentry('Doe2013')
        self.assertEqual(orig, retrieved)

    def test_pushes_paper_metadata(self):
        orig = {'docfile': 'dummy', 'tags': set(['tag', 'another']),
                'added': datetime(2012, 12, 12, 12, 12, 12, 12)}
        self.repo.push_paper(Paper.from_bibentry(fixtures.doe_bibentry,
                                                 metadata=orig))
        retrieved = self.repo.databroker.pull_metadata('Doe2013')
        self.assertEqual(orig, retrieved)

    def test_pushes_paper_metadata_set_added(self):
        orig = {'docfile': 'dummy', 'tags': set(['tag', 'another'])}
        now = datetime.now()
        self.repo.push_paper(Paper.from_bibentry(fixtures.doe_bibentry,
                                                 metadata=orig))
        retrieved = self.repo.databroker.pull_metadata('Doe2013')
        self.assertIn('added', retrieved)
        self.assertTrue(now < retrieved['added'])


class TestUpdatePaper(TestRepo):

    def test_updates_same_key(self):
        new = self.repo.pull_paper('turing1950computing')
        new.bibentry['year'] = '51'
        self.repo.push_paper(new, overwrite=True)
        self.assertEqual(new, self.repo.pull_paper('turing1950computing'))

    def test_update_new_key_removes_old(self):
        paper = self.repo.pull_paper('turing1950computing')
        self.repo.rename_paper(paper, 'Turing1950')
        with self.assertRaises(InvalidReference):
            self.repo.pull_paper('turing1950computing')
        self.assertNotIn('turing1950computing', self.repo)

    def test_update_new_key_updates(self):
        paper = self.repo.pull_paper('turing1950computing')
        self.repo.rename_paper(paper, 'Turing1950')
        self.assertEqual(paper, self.repo.pull_paper('Turing1950'))

    # TODO: should also check that associated files are updated


if __name__ == '__main__':
    unittest.main()
