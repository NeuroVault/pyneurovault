#!/usr/bin/python

"""
Test NeuroVault (object) with images and collections dataframe output
"""

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false
import pandas

def check_df(df,size_min,columns):
    assert_true(isinstance(df,pandas.core.frame.DataFrame))
    assert_true(df.shape[0] >= size_min)
    assert_true(df.columns.isin(columns).sum() == len(columns))

'''Test that API dataframe object created successfully'''
def test_NeuroVault_metadata():
    from pyneurovault import api

    # Test for all images
    print "Checking metadata extraction for images..."
    images = api.get_images()
    check_df(df=images,size_min=7000,columns=["url","name","map_type"])

    # Test for subset of images
    images = api.get_images(pks=images.image_id[0:10].tolist())
    check_df(df=images,size_min=10,columns=["url","name","map_type"])

    # Test for collections
    print "Checking metadata extraction for collections..."
    collections = api.get_collections()
    check_df(df=collections,size_min=300,columns=["used_smoothing","url","collection_id"])

    # Test get_images_and_collections
    combined_df = api.get_images_with_collections(collection_ids=[877,437])
    check_df(df=combined_df,size_min=50,columns=["url_image","collection_id","name_image","map_type","image_id"])

    # Test metadata for subset of collections
    collections = api.get_collections(pks=collections.collection_id[0:10].tolist())
    check_df(df=collections,size_min=10,columns=["used_smoothing","url","collection_id"])
    
    # Test metadata of images from specific collections
    images = api.get_images(collection_pks=collections.collection_id[0:100].tolist())
    check_df(df=images,size_min=1,columns=["url","name","map_type"])

    # Test metadata from specific DOIs
    dois = collections.DOI[collections.DOI.isnull()==False].tolist()
    results = api.collections_from_dois(dois)
    check_df(df=results,size_min=len(dois),columns=["used_smoothing","url","collection_id"])
