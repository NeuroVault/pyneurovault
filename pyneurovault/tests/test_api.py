#!/usr/bin/python

"""
Test NeuroVault (object) with images and collections dataframe output
"""

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false

'''Test that API dataframe object created successfully'''
def test_NeuroVault_object():
    from pyneurovault import api

    # Will extract all collections and images in one query to work from
    nv = api.NeuroVault()
    assert_equal(str(nv),"NeuroVault Object (nv) Includes <nv.images><nv.collections>")
