#!/usr/bin/python

"""
Test NeuroVault (object) with images and collections dataframe output
"""

import unittest
import pandas


def check_df(df, size_min, columns):
    assert isinstance(df, pandas.core.frame.DataFrame)
    assert df.shape[0] >= size_min
    assert df.columns.isin(columns).sum() == len(columns)


class TestAPI(unittest.TestCase):
    def setUp(self):
        print("\n---START----------------------------------------")

    def tearDown(self):
        print("\n---END------------------------------------------")

    def test_metadata(self):
        from pyneurovault import api

        # Test for collections
        print("Checking metadata extraction for collections...")
        collections = api.get_collections()
        check_df(
            df=collections,
            size_min=300,
            columns=["used_smoothing", "url", "collection_id"],
        )

        # Test metadata from specific DOIs
        dois = collections.DOI[collections.DOI.isnull() == False].tolist()[0:15]
        results = api.collections_from_dois(dois)
        check_df(
            df=results,
            size_min=len(dois),
            columns=["used_smoothing", "url", "collection_id"],
        )

        # Test get_images_and_collections
        combined_df = api.get_images_with_collections(collection_pks=[877, 437])
        check_df(
            df=combined_df,
            size_min=50,
            columns=[
                "url_image",
                "collection_id",
                "name_image",
                "map_type",
                "image_id",
            ],
        )

        # Test metadata for subset of collections
        collections = api.get_collections(pks=[877, 437])
        check_df(
            df=collections,
            size_min=1,
            columns=["used_smoothing", "url", "collection_id"],
        )

        # Test metadata of images from specific collections
        images = api.get_images(collection_pks=[877, 437])
        check_df(df=images, size_min=50, columns=["url", "name", "map_type"])
