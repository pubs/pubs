# -*- coding: utf-8 -*-
import unittest
import os

import testenv
import fake_env

from papers import content, filebroker, databroker, datacache

import str_fixtures
from papers import endecoder

class TestFakeFs(unittest.TestCase):
    """Abstract TestCase intializing the fake filesystem."""

    def setUp(self):
        self.fs = fake_env.create_fake_fs([content, filebroker])

    def tearDown(self):
        fake_env.unset_fake_fs([content, filebroker])


class TestDataBroker(TestFakeFs):

    def test_databroker(self):

        ende = endecoder.EnDecoder()
        page99_metadata = ende.decode_metadata(str_fixtures.metadata_raw0)
        page99_bibdata  = ende.decode_bibdata(str_fixtures.bibyaml_raw0)

        dtb = databroker.DataBroker('tmp', create=True)
        dtc = datacache.DataCache('tmp')

        for db in [dtb, dtc]:
            db.push_metadata('citekey1', page99_metadata)
            db.push_bibdata('citekey1', page99_bibdata)

            self.assertEqual(db.pull_metadata('citekey1'), page99_metadata)
            self.assertEqual(db.pull_bibdata('citekey1'), page99_bibdata)

    def test_existing_data(self):

        ende = endecoder.EnDecoder()
        page99_bibdata  = ende.decode_bibdata(str_fixtures.bibyaml_raw0)

        for db_class in [databroker.DataBroker, datacache.DataCache]:
            self.fs = fake_env.create_fake_fs([content, filebroker])
            fake_env.copy_dir(self.fs, os.path.join(os.path.dirname(__file__), 'testrepo'), 'repo')

            db = db_class('repo', create=False)

            self.assertEqual(db.pull_bibdata('Page99'), page99_bibdata)

            for citekey in ['10.1371_journal.pone.0038236', 
                            '10.1371journal.pone.0063400', 
                            'journal0063400']:
                db.pull_bibdata(citekey)
                db.pull_metadata(citekey)

            with self.assertRaises(IOError):
                db.pull_bibdata('citekey')
            with self.assertRaises(IOError):
                db.pull_metadata('citekey')

            db.copy_doc('Larry99', 'pubsdir://doc/Page99.pdf')
            self.assertTrue(content.check_file('repo/doc/Page99.pdf', fail=False))
            self.assertTrue(content.check_file('repo/doc/Larry99.pdf', fail=False))

            db.remove_doc('pubsdir://doc/Page99.pdf')
