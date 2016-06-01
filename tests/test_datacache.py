# -*- coding: utf-8 -*-
import unittest
import time

import dotdot
import fake_env

from pubs.datacache import CacheEntrySet


class FakeFileBrokerMeta(object):

    mtime = None

    def mtime_metafile(self, key):
        return self.mtime


class FakeFileBrokerBib(object):

    mtime = None

    def mtime_bibfile(self, key):
        return self.mtime


class FakeDataBrokerMeta(object):

    meta = None

    def pull_metadata(self, key):
        return self.meta

    def push_metadata(self, key, meta):
        self.meta = meta

    def push_cache(name, entries):
        if name != 'metacache':
            raise AttributeError


class FakeDataBrokerBib(object):

    bib = None

    def pull_bibentry(self, key):
        return self.bib

    def push_bibentry(self, key, bib):
        self.bib = bib

    def push_cache(name, entries):
        if name != 'bibcache':
            raise AttributeError


class TestCacheEntrySet(unittest.TestCase):

    def setUp(self):
        self.databroker_meta = FakeDataBrokerMeta()
        self.databroker_meta.filebroker = FakeFileBrokerMeta()
        self.databroker_bib = FakeDataBrokerBib()
        self.databroker_bib.filebroker = FakeFileBrokerBib()
        self.metacache = CacheEntrySet(self.databroker_meta, 'metacache')
        self.bibcache = CacheEntrySet(self.databroker_bib, 'bibcache')

    def test_metacache_does_not_call_bib_functions(self):
        with self.assertRaises(AttributeError):
            CacheEntrySet(self.databroker_bib, 'metacache')

    def test_bibcache_does_not_call_bib_functions(self):
        with self.assertRaises(AttributeError):
            CacheEntrySet(self.databroker_meta, 'bibcache')

    def test_push_pushes_to_file(self):
        self.metacache.push('a', 'b')
        self.assertEqual(self.databroker_meta.meta, 'b')
        self.bibcache.push('a', 'b')
        self.assertEqual(self.databroker_bib.bib, 'b')

    def test_push_to_cache_does_not_push_to_file(self):
        self.metacache.push_to_cache('a', 'b')
        self.assertIs(self.databroker_meta.meta, None)
        self.bibcache.push_to_cache('a', 'b')
        self.assertIs(self.databroker_bib.bib, None)

    def test_push_to_cache_pushes_to_cache(self):
        self.metacache.push_to_cache('a', 'b')
        self.assertIs(self.metacache.entries['a'].data, 'b')
        self.bibcache.push_to_cache('a', 'b')
        self.assertIs(self.bibcache.entries['a'].data, 'b')

    def test_pulls_from_file(self):
        self.databroker_meta.meta = 'b'
        value = self.metacache.pull('a')
        self.assertEqual(value, 'b')
        self.databroker_bib.bib = 'b'
        value = self.bibcache.pull('a')
        self.assertEqual(value, 'b')

    def test_pulls_from_cache(self):
        self.databroker_meta.meta = 'b'
        self.databroker_meta.filebroker.mtime = time.time()
        self.metacache.push_to_cache('a', 'c')
        self.databroker_meta.filebroker.mtime = time.time() - 1.1
        value = self.metacache.pull('a')
        self.assertEqual(value, 'c')
        self.databroker_meta.filebroker.mtime = time.time()
        self.databroker_bib.bib = 'b'
        self.databroker_bib.filebroker.mtime = time.time() - 1.1
        self.bibcache.push_to_cache('a', 'c')
        value = self.bibcache.pull('a')
        self.assertEqual(value, 'c')

    def test_pulls_outdated_from_file(self):
        self.databroker_meta.meta = 'b'
        self.databroker_meta.filebroker.mtime = time.time()
        self.metacache.push_to_cache('a', 'c')
        self.databroker_meta.filebroker.mtime = time.time() + 1.1
        value = self.metacache.pull('a')
        self.assertEqual(value, 'b')
        self.databroker_bib.bib = 'b'
        self.databroker_bib.filebroker.mtime = time.time()
        self.bibcache.push_to_cache('a', 'c')
        self.databroker_bib.filebroker.mtime = time.time() + 1.1
        value = self.bibcache.pull('a')
        self.assertEqual(value, 'b')


    def test_is_outdated_when_unknown_citekey(self):
        self.assertTrue(self.metacache._is_outdated('a'))

    def test_is_outdated_when_newer_mtime(self):
        # Actually tests for mtime in future
        self.bibcache.push_to_cache('a', 'b')
        self.databroker_meta.filebroker.mtime = time.time() + 1.1
        self.assertTrue(self.metacache._is_outdated('a'))

    def test_is_not_outdated_when_older_mtime(self):
        # Actually tests for mtime in future
        self.databroker_meta.filebroker.mtime = time.time()
        self.metacache.push_to_cache('a', 'b')
        self.databroker_meta.filebroker.mtime = time.time() - 1.1
        self.assertFalse(self.metacache._is_outdated('a'))
