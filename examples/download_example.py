#!/usr/bin/env python2

# This script will use the pyneurovault module to download meta information about images and collections from NeuroVault

from pyneurovault import api

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()

# If we want to get either data frame, or combined
nv.get_images_df()
nv.get_collections_df()
nv.get_images_with_collections_df()

# Get unique cognitive atlas contrasts and counts
contrasts = nv.get_contrasts()

# Download images, collections, or both
nv.export_images_tsv("/home/vanessa/Desktop/images.tsv")
nv.export_collections_tsv("/home/vanessa/Desktop/collections.tsv")

# Download raw images to file
outfolder = "/home/vanessa/Desktop"
standard = "/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz"
nv.download_and_resample(outfolder,standard)
