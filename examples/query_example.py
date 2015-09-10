#!/usr/bin/env python2

# This script will use the pyneurovault module to perform single REST queries from NeuroVault. 

from pyneurovault.api import collections_from_dois, images_from_collections, get_images_with_collections
from pyneurovault import pubmed as pm

# 1) SINGLE REST QUERY EXAMPLE
# Here is a doi that we are interested in
doi = "10.1016/j.neurobiolaging.2012.11.002"

# A DOI is associated with a collection. Download it.
collection = collections_from_dois(doi)

# Here is the identifier
# collection[0]["id"]
# 77

# Get the images
images = images_from_collections(collection[0]["id"])[0]

# Here are the file URLs for the images, as well as contrasts 
# and cognitive atlas contrasts IDs. (we can use this later to tag to CA)
for image in images:
  print "<file:%s><contrast:%s><ca-contrast:%s>" %(image["file"],image["contrast_definition"],image["contrast_definition_cogatlas"])
 
# We now want to use the doi to look up the pmid
pubmed = pm.Pubmed(email="myname@email.com")
article = pubmed.get_single_article(doi)
pmid = article.get_pmid()

# 2) SEARCH FIELD ACROSS ALL COLLECTIONS OR DATA
df = get_collections()
result = search(df=df,column_name="description_collection",search_string="OpenfMRI")



