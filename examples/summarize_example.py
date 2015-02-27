from pyneurovault import api

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()
data = nv.get_images_with_collections_df()

# Get unique cognitive atlas contrasts and counts
nv.get_contrast_counts()
nv.get_cognitive_atlas_paradigm_counts()
nv.get_modality_counts()
nv.get_map_type_counts()
nv.get_collection_counts()

# Find images of a particular map type, Z images (also can specify modality)
image_ids = nv.get_image_ids(map_type="Z",modality=None)

# Download images (also save output file of meta data)
outfolder = "/scratch/users/russpold/data/NEUROVAULT/dump"
standard = "/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz"
nv.download_and_resample(outfolder,standard,image_ids=image_ids)
