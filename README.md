# pyneurovault

python wrapper for NeuroVault api (in dev)

Currently supports: 
- downloading all image and collections data into tables
- counting unique cognitive atlas contrasts
- downloading all resampled images
- decoding with neurosynth terms

Query functionality will be added.

### Installation

    git clone https://github.com/poldracklab/pyneurovault
    cd pyneurovault
    sudo python setup.py install

### Example

    from pyneurovault import api

    # Will extract all collections and images in one query to work from
    nv = api.NeuroVault()

    # Get unique cognitive atlas contrasts and counts
    contrasts = nv.get_contrasts()

    # Download images to file
    outfolder = "/home/vanessa/Documents/Work/BRAINBEHAVIOR/mrs"

    # Now use R/summarizeData.R to explore distributions, etc.
    nv.downloadImages(outfolder)
