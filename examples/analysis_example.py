#!/usr/bin/env python2

# This script will use the pyneurovault module to download meta information about images and collections from NeuroVault

from pyneurovault import api
import pandas as pd
import numpy as np
import pylab as plt
import nibabel as nb
from nilearn.plotting.img_plotting import plot_anat
from pyneurovault.nsynth import get_neurosynth_terms
from pyneurovault.analysis import get_frequency_map

# Use a joblib memory, to avoid depending on an Internet connection
from joblib import Memory
mem = Memory(cachedir='/tmp/neurovault_analysis/cache')

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()

# 2) SEARCH FIELD ACROSS ALL COLLECTIONS OR DATA
df = nv.get_images_with_collections_df()
openfmri = nv.search(df=df,column_name="description_collection",search_string="OpenfMRI")
hcp = nv.filter(df=df,column_name="collection_id",field_value=457)
combined_df = openfmri.append(hcp)
print combined_df[['DOI', 'url_collection', 'name_image', 'file']]

# Download and resample
# you can download to tmp folder /tmp/neurovault_analysis
dest_dir = "/home/vanessa/Documents/Work/BRAINMETA/REVERSE_INFERENCE/mr"
target = "/usr/share/fsl/data/standard/MNI152_T1_2mm.nii.gz"
image_ids = combined_df.image_id.tolist()
download_table = nv.download_and_resample(dest_dir, target, image_ids=image_ids)
download_table.to_csv('%s/download_table.tsv' % dest_dir, encoding='utf8',sep="\t")
combined_df.to_csv('%s/metadata.tsv' % dest_dir, encoding='utf8',sep="\t")

# Example 1: Cognitive Decoding with NeuroSynth
terms_df = get_neurosynth_terms(combined_df)
print combined_df["name_collection"].value_counts()
combined_df = combined_df.merge(terms_df, on=['image_id', ])


# 3) Do analysis

#--------------------------------------------------
# Plot a map of frequency of activation
freq_nii = get_frequency_map(combined_df, dest_dir, target)
freq_nii.to_filename("%s/freq_map.nii.gz" %dest_dir)
display = plot_anat("/usr/share/fsl/data/standard/MNI152_T1_2mm.nii.gz",
                    display_mode='z',
                    cut_coords=np.linspace(-30, 60, 7))
display.add_overlay(freq_nii, vmin=0, cmap=plt.cm.hot,colorbar=True)
display._colorbar_ax.set_yticklabels(["% 3i" % float(t.get_text()) for t in display._colorbar_ax.yaxis.get_ticklabels()])
display.title('Percentage of activations (Z or T > 3)')
display.savefig('%s/activation_frequency.png' %(dest_dir))
display.savefig('%s/activation_frequency.pdf' %(dest_dir))

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
  plt.savefig('%s/term_distribution.pdf' %(dest_dir))
  plt.show()
