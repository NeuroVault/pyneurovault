#!/usr/bin/env python

'''

analysis: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


'''

__author__ = ["Chris Filo Gorgolewski","Gael Varoquaux", "Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

import os
import numpy as np
import nibabel as nb
from pyneurovault.utils import (
    get_standard_brain, 
    split_filename
)

def get_frequency_map(images_df, dest_dir, target):
    mask_img = get_standard_brain()
    mask = nb.load(mask_img).get_data().astype(np.bool)

    target_nii = nb.load(target)
    resampled_path = os.path.join(dest_dir, "resampled")
    freq_map_data = np.zeros(target_nii.shape)

    n_images = 0
    for row in images_df.iterrows():
        
        _, _, ext = split_filename(row[1]['file'])
        orig_file = os.path.join(
            resampled_path, "%06d%s" % (row[1]['image_id'], ext))
        resampled_nii = nb.load(orig_file)
        try:
            data = resampled_nii.get_data().squeeze()
        except IOError:
            continue
        data[np.isnan(data)] = 0
        data[np.logical_not(mask)] = 0
        data = np.abs(data)

        # Keep only things that are very significant
        data = data > 3
        if len(data.shape) == 4:
            for d in np.rollaxis(data, -1):
                freq_map_data += (d != 0)
                n_images += 1
        else:
            freq_map_data += data
            n_images += 1

    freq_map_data *= 100. / n_images
    return nb.Nifti1Image(freq_map_data, target_nii.get_affine())
