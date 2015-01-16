#!/usr/bin/env python

"""

api: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


"""

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/09/09 $"
__license__ = "BSD"

import json
import pandas as pd
import numpy as np
import pylab as plt
import nibabel as nb
import urllib, os
from utils import mkdir_p, get_url
from nilearn.image import resample_img
from pandas.io.json import json_normalize
from urllib2 import Request, urlopen, HTTPError
from nipype.utils.filemanip import split_filename
from nilearn.plotting.img_plotting import plot_anat
from nilearn.masking import compute_background_mask, _extrapolate_out_mask


def get_frequency_map(images_df, dest_dir, target):
  mask_img = 'gm_mask.nii.gz'
  mask = nb.load(mask_img).get_data().astype(np.bool)

  target_nii = nb.load(target)
  resampled_path = os.path.join(dest_dir, "resampled")
  freq_map_data = np.zeros(target_nii.shape)

  n_images = 0
  for row in combined_df.iterrows():
    _, _, ext = split_filename(row[1]['file'])
    orig_file = os.path.join(resampled_path,"%06d%s" % (row[1]['image_id'], ext))
    nb.load(orig_file)
    if not os.path.exists(orig_file):
      urllib.urlretrieve(row[1]['file'], orig_file)

      resampled_nii = resample_img(orig_file, target_nii.get_affine(),target_nii.shape,interpolation="nearest")
      data = resampled_nii.get_data().squeeze()
      data[np.isnan(data)] = 0
      data[np.logical_not(mask)] = 0
      data = np.abs(data)

      # Keep only things that are very significant
      data = data > 3
      if len(data.shape) == 4:
        for d in np.rollaxis(data, -1):
          freq_map_data += (d != 0)
          n_images +=1
        else:
          freq_map_data += data
          n_images += 1

      freq_map_data *= 100. / n_images
      return nb.Nifti1Image(freq_map_data, target_nii.get_affine())

