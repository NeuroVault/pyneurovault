# Get all dois from collections using the NeuroVault API

from pyneurovault.api import get_collections

# This will return a pandas data frame
collections = get_collections()

# Take a look at the fields
collections.columns

# Retrieve the "DOI" column, remove null values
dois = collections["DOI"][collections["DOI"].isnull()==False]

# Export them to a tab separated file
dois.to_csv("/home/vanessa/Desktop/dois.tsv",sep="\t",index=None)

# Or turn into a list for something else
dois.tolist()
