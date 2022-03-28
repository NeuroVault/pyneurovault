# Get all dois from collections using the NeuroVault API

from pyneurovault.api import get_collections, export_collections_tsv

# This will return a pandas data frame
collections = get_collections()

# Take a look at the fields
collections.columns

# Export collections tsv
export_collections_tsv("collections.tsv", collections)

# Retrieve the "DOI" column, remove null values
dois = collections["DOI"][collections["DOI"].isnull() == False]

# Export them to a tab separated file
dois.to_csv("dois.tsv", sep="\t", index=None)

# Or turn into a list for something else
dois.tolist()
