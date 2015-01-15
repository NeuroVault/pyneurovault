#!/usr/bin/env python2

# This script will use the pyneurovault module to download meta information about images and collections from NeuroVault

from pyneurovault import api

# Will extract all collections and images in one query to work from
nv = api.NeuroVault()

# Get unique cognitive atlas contrasts and counts
contrasts = nv.get_contrasts()

# Download images to file
outfolder = "/home/vanessa/Documents/Work/BRAINBEHAVIOR/mrs"

# Now use R/summarizeData.R to explore distributions, etc.
nv.downloadImages(outfolder)
