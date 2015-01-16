#!/usr/bin/env python2

# This script will use the pyneurovault module to download meta information about images and collections from NeuroVault

from pyneurovault import api
from pyneurovault.nsynth import get_neurosynth_terms
from pyneurovault.analysis import get_frequency_map

# Use a joblib memory, to avoid depending on an Internet connection
from joblib import Memory
mem = Memory(cachedir='/tmp/neurovault_analysis/cache')

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()

# Get the combined image / collections data frame
combined_df = mem.cache(nv.get_images_with_collections_df)()

#--------------------------------------------------
# IMPORTANT: This code functionality will be integrated into API (analysis.py)
# Code below "works" but was generated for NeuroVault version in 9/2014

# Here is how to eliminate maps from analysis - this has not been updated since 9/2014
# The following maps are not brain maps
faulty_ids = [96, 97, 98]
# And the following are crap
faulty_ids.extend([338, 339])
# 335 is a duplicate of 336
faulty_ids.extend([335, ])
combined_df = combined_df[~combined_df.image_id.isin(faulty_ids)]

print combined_df[['DOI', 'url_collection', 'name_image', 'file']]

#restrict to Z-, F-, or T-maps
combined_df = combined_df[combined_df['map_type'].isin(["Z","F","T"])]
terms_df = get_neurosynth_terms(combined_df)
print combined_df["name_collection"].value_counts()
combined_df = combined_df.merge(terms_df, on=['image_id', ])

dest_dir = "/tmp/neurovault_analysis"
target = "/usr/share/fsl/data/standard/MNI152_T1_2mm.nii.gz"

# IMPORTANT: Not tested beyond this point!
combined_df = mem.cache(nv.download_and_resample)(combined_df,dest_dir, target)

import pandas as pd
import numpy as np
import pylab as plt
import nibabel as nb
from nilearn.plotting.img_plotting import plot_anat

# Now remove -3360, -3362, and -3364, that are mean images, and not Z scores
not_Zscr = [-3360, -3362, -3364]
combined_df = combined_df[~combined_df.image_id.isin(not_Zscr)]

combined_df.to_csv('%s/metadata.csv' % dest_dir, encoding='utf8')


#--------------------------------------------------
# Plot a map of frequency of activation
freq_nii = get_frequency_map(combined_df, dest_dir, target)
freq_nii.to_filename("/tmp/freq_map.nii.gz")

display = plot_anat("/usr/share/fsl/data/standard/MNI152_T1_2mm.nii.gz",
                    display_mode='z',
                    cut_coords=np.linspace(-30, 60, 7))
display.add_overlay(freq_nii, vmin=0, cmap=plt.cm.hot,colorbar=True)
display._colorbar_ax.set_yticklabels(["% 3i" % float(t.get_text())
  for t in display._colorbar_ax.yaxis.get_ticklabels()])
    display.title('Percentage of activations (Z or T > 3)')
    display.savefig('activation_frequency.png')
    display.savefig('activation_frequency.pdf')

#--------------------------------------------------
# Plot the frequency of occurence of neurosynth terms
# Use the terms from neurosynth to label the ICAs
terms = combined_df[[c for c in combined_df.columns if c.startswith('neurosynth decoding')]]
terms = terms.fillna(0)
term_matrix = terms.as_matrix()

# Labels that have a negative correlation are not present in the map
term_matrix[term_matrix < 0] = 0

term_names = [c[20:] for c in combined_df.columns if c.startswith('neurosynth decoding')]

plt.figure(figsize=(5, 20))
plt.barh(np.arange(len(term_names)), term_matrix.sum(axis=0))
plt.axis('off')
plt.axis('tight')
plt.tight_layout()
for idx, name in enumerate(term_names):
  plt.text(.1, idx + .1, name)
  plt.savefig('term_distribution.pdf')
  plt.show()
