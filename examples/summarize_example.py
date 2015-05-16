from pyneurovault import api

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()

# Get unique cognitive atlas contrasts and counts
nv.get_paradigm_counts()
nv.get_modality_counts()
nv.get_map_type_counts()
nv.get_collection_counts()

# Find images of a particular map type, Z images (also can specify modality=)
image_ids = nv.get_image_ids(map_type="Z")

# Download images (also save output file of meta data)
outfolder = "/home/vanessa/Desktop/Z"
standard = "/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz"
download_data = nv.download_images(outfolder,standard,image_ids=image_ids)
download_data.to_pickle("/home/vanessa/Desktop/Z/image_data.pkl")
