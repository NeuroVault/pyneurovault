#!/usr/bin/env python2

# This script will use the pyneurovault module to perform single REST queries from NeuroVault. This strategy is intended for smaller/single queries that use the REST api. For larger analysis to download all of NeuroVault meta at once, see download_example.py.

from pyneurovault import api, pubmed as pm

# Here is a doi that we are interested in
doi = "10.1016/j.neurobiolaging.2012.11.002"

# A DOI is associated with a collection. Download it.
collection = api.collection_from_doi(doi)

# Get the images
images = api.images_from_collection(collection)

# Here are the file URLs for the images, as well as contrasts 
# and cognitive atlas contrasts IDs. (we can use this later to tag to CA)
for image in images:
  print "<file:%s><contrast:%s><ca-contrast:%s>" %(image["file"],image["contrast_definition"],image["contrast_definition_cogatlas"])
 
# We now want to use the doi to look up the pmid
pubmed = pm.Pubmed(email="myname@email.com")
article = pubmed.get_single_article(doi)
pmid = article.get_pmid()




