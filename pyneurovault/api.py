#!/usr/bin/env python

"""

api: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


"""
import os
import json
import string
import urllib
import urllib2
import numpy as np
import pandas as pd
import nibabel as nb
import numpy as np
from nilearn.image import resample_img
from pyneurovault.utils import DataJson, get_json, mkdir_p, get_url
from nipype.utils.filemanip import split_filename
from nilearn.masking import compute_background_mask, _extrapolate_out_mask

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

# REST API Wrapper Functions
def collections_from_dois(dois):
  if isinstance(dois,str): return DataJson("http://neurovault.org/api/collections/?DOI=%s" %(dois))
  else:
    collections = []
    for doi in dois:
      collections.append(DataJson("http://neurovault.org/api/collections/?DOI=%s" %(doi)))
    return collections

# Functions to manipulate data returned from REST
def images_from_collections(collections):
  if isinstance(collections,list):
    images = []
    for collection in collections:
      images.append(collection.data["images"][0])
    return images
  else: return collections.data["images"][0]

  
# NeuroVault Analysis API
"""A NeuroVault object holds images and collections.
For doing multiple queries for which single REST does not make sense
"""
class NeuroVault:
  def __init__(self):
    self.images = self.get_images()                
    self.collections = self.get_collections()      
    print self

  def __str__(self):
    """Download meta information about images in database"""
    return "NeuroVault Object (nv) Includes <nv.images,DataJson><nv.collections,DataJson>}"

# Summary and Counting Functions

  def get_contrast_counts(self):
    """Get counts of contrasts"""
    return self.images.data["contrast_definition_cogatlas"].value_counts()

  def get_cognitive_atlas_paradigm_counts(self):
    """Get counts of cognitive atlas paradigms"""
    return self.images.data["cognitive_paradigm_cogatlas"].value_counts()

  def get_modality_counts(self):
    """Get counts of modality types"""
    return self.images.data["modality"].value_counts()

  def get_map_type_counts(self):
    """Get counts of image map types"""
    return self.images.data["map_type"].value_counts()

  def get_collection_counts(self):
    return self.images.data["collection_id"].value_counts()

# Database Query and table preparation

  def get_images(self,pks=None):
    """Download metadata about images stored in NeuroVault and return it as a pandas DataFrame"""
    print "Extracting NeuroVault images meta data..."
    if not pks:
        images = get_json("images")
    else:
        images = get_json("images",pks)            
    images['collection'] = images['collection'].apply(lambda x: int(x.split("/")[-2]))
    images['image_id'] = images['url'].apply(lambda x: int(x.split("/")[-2]))
    images.rename(columns={'collection':'collection_id'}, inplace=True)
    return images

  def get_collections(self,pks=None):
    """Download metadata about collections/papers stored in NeuroVault and return it as a pandas DataFrame"""
    print "Extracting NeuroVault collections meta data..."
    if not pks:
        collections = get_json("collections")
    else:
        collections = get_json("collections",pks)            
    collections.rename(columns={'id':'collection_id'}, inplace=True)
    collections.set_index("collection_id")
    return collections

  def get_collections_df(self):
    """Return just collections data frame"""
    return self.collections.data

  def get_images_df(self):
    """Return just images data frame"""
    return self.images.data

  def get_images_with_collections_df(self):
    """Downloads metadata about images/statistical maps stored in NeuroVault and enriches it with metadata of the corresponding collections. The result is returned as a pandas DataFrame"""
    collections_df = self.get_collections_df()
    images_df = self.get_images_df()
    combined_df = pd.merge(images_df, collections_df, how='left', on='collection_id',suffixes=('_image', '_collection'))
    return combined_df

# Search

  def search(self,df,column_name,search_string):
    """Search a data frame field for a string of choice"""
    tmp_df = df[df[column_name].isnull() == False]
    return tmp_df[tmp_df[column_name].str.contains(search_string)]

  def filter(self,df,column_name,field_value):
    """Filter a data frame to only include matches with field value in column_name"""
    tmp_df = df[df[column_name].isnull() == False]
    return tmp_df[tmp_df[column_name]==field_value]

  def get_image_ids(self,map_type=None,modality=None):
    """Get image ids with modality and map type filters"""
    df = self.images.data.copy()
    if map_type:
      df = df.loc[df.map_type==map_type]
    elif modality:
      df = df.loc[df.modlity==modality] 
    return df.image_id.tolist()

# Export

  def export_images_tsv(self,output_file):
    """Export images to tab separated value file (tsv)"""
    self.images.data.to_csv(output_file,encoding="utf-8",sep="\t")

  def export_collections_tsv(self,output_file):
    """Export collections to tab separated value file (tsv)"""
    self.collections.data.to_csv(output_file,encoding="utf-8",sep="\t")

# Image download

  def download_and_resample(self, dest_dir, target,collection_ids=None,image_ids=None):
    """Downloads all stat maps and resamples them to a common space"""
    target_nii = nb.load(target)
    orig_path = os.path.join(dest_dir, "original")
    mkdir_p(orig_path)
    resampled_path = os.path.join(dest_dir, "resampled")
    mkdir_p(resampled_path)
    combined_df = self.get_images_with_collections_df()
    # If the user has specified specific images
    if image_ids:
      combined_df = combined_df.loc[combined_df.image_id.isin(image_ids)]
    # If the user wants to subset to a set of collections
    if collection_ids:
      if isinstance(collection_ids,str): collection_ids = [collection_ids]
      combined_df = combined_df[combined_df['collection_id'].isin(collection_ids)]
    out_df = combined_df.copy()

    for row in combined_df.iterrows():
      # Downloading the file to the "original" subfolder
      _, _, ext = split_filename(row[1]['file'])
      orig_file = os.path.join(orig_path, "%04d%s" % (row[1]['image_id'], ext))
      if not os.path.exists(orig_file):
        try:
          print "Downloading %s" % orig_file
          urllib.urlretrieve(row[1]['file'], orig_file)

          # Compute the background and extrapolate outside of the mask
          print "Extrapolating %s" % orig_file
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
          print "Resampling %s" % orig_file
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
          print "Error downloading image id %s, retry this image." %(row[1]["image_id"])
    return out_df


def main():
  print __doc__

if __name__ == "__main__":
  main()
