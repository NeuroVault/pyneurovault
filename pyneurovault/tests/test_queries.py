#!/usr/bin/python

"""
Test NeuroVault REST API Queries
"""

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false
from pyneurovault.api import  collections_from_dois, images_from_collections

'''Test REST API Queries'''
def test_queries():
    doi = "10.1016/j.neurobiolaging.2012.11.002"

    # A DOI is associated with a collection. Download it.
    collection = collections_from_dois(doi)
    assert_equal(len(collection),1)

    # Get the images
    images = images_from_collections(collection[0]["id"])
    assert_true(len(images[0]) > 1)
 
