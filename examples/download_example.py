#!/usr/bin/env python2

# This script will use the pyneurovault module to download meta information about images and collections from NeuroVault.

from pyneurovault import api

# Get a collection
collection = api.get_collections(pks=457)
# collection.collection_id is 457

# Get all images
images = api.get_images()

# Get all images meta data for a collection
images = api.get_images(collection_pks=457)

# Remove images that are thresholded
images = api.filter(df=images, column_name="is_thresholded", field_value=False)

# Not in MNI
images = api.filter(df=images, column_name="not_mni", field_value=False)

# Just fMRI bold
images = api.filter(df=images, column_name="modality", field_value="fMRI-BOLD")

# Download images, collections, or both
api.export_images_tsv("images.tsv", images)
api.export_collections_tsv("collections.tsv", collection)

# Download all images to file, resample to target
outfolder = os.getcwd()
standard = "pyneurovault/data/MNI152_T1_2mm_brain.nii.gz"
api.download_images(dest_dir=outfolder, images_df=images, target=standard)

# If you don't want to resample
api.download_images(dest_dir=outfolder, images_df=images, resample=False)
