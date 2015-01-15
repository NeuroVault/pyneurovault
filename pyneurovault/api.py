#!/usr/bin/env python

"""

api: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


"""

from utils import DataJson
import string
import urllib2
import json
import numpy as np

__author__ = ["Poldracklab [vsochat@stanford.edu]"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/09/09 $"
__license__ = "Python"


'''A NeuroVault object holds images and collections'''
class NeuroVault:
    def __init__(self):
      self.images = self.__getMeta__()                  # get image meta information
      self.collections = self.__getCollections__()      # get collections meta information from json
      print self

    """Download meta information about images in database"""
    def __str__(self):
      return "NeuroVault Object (nv) Includes <nv.images,DataJson><nv.collections,DataJson>}"

    """Get counts of contrasts"""
    def get_contrasts(self):
      return self.images.data["contrast_definition_cogatlas"].value_counts()

    """Download image data to file"""
    def downloadImages(self,outdir):
      import urllib; import ntpath
      if not outdir:
        print "Downloading images to current working directory."
      else:
        print "Downloading images to " + outdir
        if outdir[-1] not in ["\\","/"]:
          outdir = outdir + "/"
        filegetter = urllib.URLopener()
        for image in self.images.data["file"].values():
          filename = ntpath.basename(image)
          # Get the collection id
          collection_id = self.images.data["collection"][image].split("/")[-2].encode("utf-8")
          output_image = outdir + collection_id + "_" + filename
          if not os.path.isfile(output_image):
            print "Downloading " + filename + "."
            try:
              filegetter.retrieve(image, output_image)
            except:
              print "Error downloading " + image + ". Skipping!"

# Internal functions * * * *

    """Download image meta"""
    def __getMeta__(self):
      print "Extracting NeuroVault images meta data..."
      # Return a DataJson object with all fields
      myjson = DataJson("http://neurovault.org/api/images/?format=json","file")
      print "Images:"
      print myjson
      return myjson

    """Download collection meta"""
    def __getCollections__(self):
      print "Extracting NeuroVault collections meta data..."
      # Return a DataJson object with all fields
      myjson = DataJson("http://neurovault.org/api/collections/?format=json","id")
      print "Collections, see\n NeuroVault.collections.fields\nNeuroVault.collections.data"
      print myjson
      return myjson

def main():
  print __doc__

if __name__ == "__main__":
  main()
