# pyneurovault

python wrapper for NeuroVault api (in dev)

Currently supports: 
- downloading all image and collections data into tables
- counting unique cognitive atlas contrasts
- downloading all resampled images
- decoding with neurosynth terms

Query functionality will be added.

### Installation

    pip install git+https://github.com/NeuroVault/pyneurovault

### Example

    # If we want to get either data frame, or combined
    nv.get_images_df()
    nv.get_collections_df()
    nv.get_images_with_collections_df()

    # Get unique cognitive atlas contrasts and counts
    contrasts = nv.get_contrasts()

    # Download raw images to file
    outfolder = "/home/vanessa/Desktop"
    standard = "/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz"
    nv.download_and_resample(outfolder,standard)
