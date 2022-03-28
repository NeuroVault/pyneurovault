#!/usr/bin/python

"""
Test NeuroVault REST API Queries
"""

from numpy.testing import assert_equal

from pyneurovault.api import collections_from_dois
import unittest


class TestQueries(unittest.TestCase):
    def setUp(self):
        print("\n---START----------------------------------------")

    def tearDown(self):
        print("\n---END------------------------------------------")

    def test_queries(self):
        """Test REST API Queries"""
        doi = "10.1016/j.neurobiolaging.2012.11.002"

        # A DOI is associated with a collection. Download it.
        collection = collections_from_dois(doi)
        assert_equal(collection.shape[0], 1)
        collections = collections_from_dois([doi, doi])
        assert_equal(collections.shape[0], 2)
