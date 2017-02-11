#!/usr/bin/env python

'''

api: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


'''

import nibabel as nb

from nilearn.masking import (
    compute_background_mask, 
    _extrapolate_out_mask
)

from nilearn.image import resample_img
import numpy as np
import os
import pandas
import string
import sys

from pyneurovault.utils import (
    get_json, 
    get_json_df, 
    mkdir_p, 
    get_url, 
    split_filename
)

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


__author__ = ["Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

# Summary and Counting Functions
def get_field_counts(df,field):
    """Get counts for a field"""
    return images[field].value_counts()

def collections_from_dois(dois,limit=100):
    if isinstance(dois,str): 
        dois = [dois]
    results = pandas.DataFrame()
    for doi in dois:
        params = check_params({"DOI":doi},limit)
        results = results.append(get_data(data_type="collections",params=params))
    results.index = results.collection_id
    return results

# Database Query and table preparation
def get_data(data_type,pks=None,params=None,extend_url=None):
    """General get function for use by collections and images"""
    print("Extracting NeuroVault %s meta data..." %(data_type))
    if not pks:
        data = get_json_df(data_type=data_type,params=params,extend_url=extend_url)
    else:
        data = get_json_df(data_type=data_type,pks=pks,params=params,extend_url=extend_url)  
    if extend_url == "images" or data_type == "images":          
        data.rename(columns={'id':'image_id'}, inplace=True)
    else:
        data.rename(columns={'id':'collection_id'}, inplace=True) 
    return data

# Get functions
def get_images(pks=None,collection_pks=None,limit=100,params={}):
    """Download metadata about images stored in NeuroVault and return it as a pandas DataFrame
       pks: a single or list of primary keys of images
       collection_pks: optional list of collection keys to limit images to. If specified, pks is ignored 
       limit: maximum number of results to return per query [default 1000]
       params: optional dictionary of additional arguments to add (eg, {"param":"value"}
    """
    params = check_params(params,limit)
    if collection_pks:
        images = get_data(data_type="collections",pks=collection_pks,params=params,extend_url="images")
    else:
        images = get_data(data_type="images",pks=pks,params=params)
    if "collection" in images.columns:
        images['collection_id'] = images['collection'].apply(lambda x: int(x.split("/")[-2]))
    return images

# Get collection metadata
def get_collections(pks=None,limit=100,params={}):
    """Download metadata about collections/papers stored in NeuroVault and return it as a pandas DataFrame
       pks: a single or list of primary keys of collections
       limit: maximum number of results to return per query [default 1]
       params: optional dictionary of additional arguments to add (eg, {"param":"value"}
    """
    params = check_params(params,limit)
    collections = get_data(data_type="collections",pks=pks,params=params)
    collections.set_index("collection_id")
    return collections

def check_params(params,limit):
    if not isinstance(params,dict):
        print("Please provide params variable as a dictionary.")
        return
    params.update({"limit":limit})
    return params

# Get images associated with one or more collections, return data frame with both
def get_images_with_collections(collection_pks=None):
    """Downloads metadata about images/statistical maps stored in NeuroVault and enriches it with metadata of the corresponding collections. The result is returned as a pandas DataFrame
       collection_pks: primary keys for collections. If not specified, will return all collections, all images
    """
    collections_df = get_collections(pks=collection_pks)
    images_df = get_images(collection_pks=collection_pks)
    combined_df = pandas.merge(images_df, collections_df, how='left', on='collection_id',suffixes=('_image', '_collection'))
    return combined_df

# Search
def search(df,column_name,search_string):
    """Search a data frame field for a string of choice"""
    tmp_df = df[df[column_name].isnull() == False]
    return tmp_df[tmp_df[column_name].str.contains(search_string)]

def filter(df,column_name,field_value):
    """Filter a data frame to only include matches with field value in column_name"""
    tmp_df = df[df[column_name].isnull() == False]
    return tmp_df[tmp_df[column_name]==field_value]

def get_image_ids(map_type=None,modality=None):
    """Get image ids with modality and map type filters"""
    df = get_images()
    if map_type:
        df = df.loc[df.map_type==map_type]
    elif modality:
        df = df.loc[df.modlity==modality] 
    return df.image_id.tolist()

# Export
def export_images_tsv(output_file,images=None):
    """Export images to tab separated value file (tsv)"""
    if not isinstance(images,pandas.DataFrame):
        images = get_images()
    images.to_csv(output_file,encoding="utf-8",sep="\t")

def export_collections_tsv(output_file,collections=None):
    """Export collections to tab separated value file (tsv)"""
    if not isinstance(collections,pandas.DataFrame):
        collections = get_collections()
    collections.to_csv(output_file,encoding="utf-8",sep="\t")

# Image download
def download_images(dest_dir,images_df=None,target=None,resample=True):
    """Downloads images dataframe and resamples them to a common space"""
    orig_path = os.path.join(dest_dir, "original")
    mkdir_p(orig_path)
    if resample == True:
        if not target:
            print("To resample you must specify a target!")
            return
        resampled_path = os.path.join(dest_dir, "resampled")
        mkdir_p(resampled_path)
        target_nii = nb.load(target)  

    if not isinstance(images_df,pandas.DataFrame):
        images_df = get_images()

    out_df = images_df.copy()

    for row in images_df.iterrows():
        # Downloading the file to the "original" subfolder
        _, _, ext = split_filename(row[1]['file'])
        orig_file = os.path.join(orig_path, "%04d%s" % (row[1]['image_id'], ext))
        if not os.path.exists(orig_file):
            try:
                print ("Downloading %s" % orig_file)
                urlretrieve(row[1]['file'], orig_file)

                if resample == True:
                    # Compute the background and extrapolate outside of the mask
                    print("Extrapolating %s" % orig_file)
                    niimg = nb.load(orig_file)
                    affine = niimg.get_affine()
                    data = niimg.get_data().squeeze()
                    niimg = nb.Nifti1Image(data, affine,header=niimg.get_header())
                    bg_mask = compute_background_mask(niimg).get_data()
                    # Test if the image has been masked:
                    out_of_mask = data[np.logical_not(bg_mask)]
                    if np.all(np.isnan(out_of_mask)) or len(np.unique(out_of_mask)) == 1:
                        # Need to extrapolate
                        data = _extrapolate_out_mask(data.astype(np.float), bg_mask,iterations=3)[0]
                    niimg = nb.Nifti1Image(data, affine,header=niimg.get_header())
                    del out_of_mask, bg_mask
                    # Resampling the file to target and saving the output in the "resampled" folder
                    resampled_file = os.path.join(resampled_path,"%06d%s" % (row[1]['image_id'], ext))
                    print("Resampling %s" % orig_file)
                    resampled_nii = resample_img(niimg, target_nii.get_affine(),target_nii.shape)
                    resampled_nii = nb.Nifti1Image(resampled_nii.get_data().squeeze(),
                                                   resampled_nii.get_affine(),
                                                     header=niimg.get_header())
                    if len(resampled_nii.shape) == 3: 
                        resampled_nii.to_filename(resampled_file)
                    else:
                        # We have a 4D file
                        assert len(resampled_nii.shape) == 4
                        resampled_data = resampled_nii.get_data()
                        affine = resampled_nii.get_affine()
                        for index in range(resampled_nii.shape[-1]):
                            # First save the files separately
                            this_nii = nb.Nifti1Image(resampled_data[..., index],affine)
                            this_id = int("%i%i" % (-row[1]['image_id'], index))
                            this_file = os.path.join(resampled_path,"%06d%s" % (this_id, ext))
                            this_nii.to_filename(this_file)
                            # Second, fix the dataframe
                            out_df = out_df[out_df.image_id != row[1]['image_id']]
                            this_row = row[1].copy()
                            this_row.image_id = this_id
                            out_df = out_df.append(this_row)
            except:
                print("Error downloading image id %s, retry this image." %(row[1]["image_id"]))
    return out_df
