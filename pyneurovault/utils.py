#!/usr/bin/env python

"""

utils: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api

"""

import os
import json
import errno
import urllib2
import pandas
import numpy as np
from pandas.io.json import read_json
from urllib2 import Request, urlopen, HTTPError

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"


# Get standard brains

def get_standard_brain():
  cwd = os.path.abspath(os.path.split(__file__)[0])
  return "%s/MNI152_T1_2mm_brain.nii.gz" %(cwd)

def get_standard_mask():
  cwd = os.path.abspath(os.path.split(__file__)[0])
  return "%s/MNI152_T1_2mm_brain_mask.nii.gz" %(cwd)


# File operations 

def mkdir_p(path):
  try:
      os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

def get_url(url):
  request = Request(url)
  response = urlopen(request)
  return response.read()


def get_json(data_type,pks=None):
    if pks==None:  # May not be feasible call if database is too big
         images = get_url("http://neurovault.org/api/%s/?format=json" %(data_type))
    else:
        if isinstance(pks,str): pks = [pks]
        images = "["
        for p in range(0,len(pks)):
            pk = pks[p]
            print "Retrieving %s %s..." %(data_type[0:-1],pk)
            try:
                tmp = get_url("http://neurovault.org/api/images/%s/?format=json" %(pk))
                if p!=0:
                    images = "%s,%s" %(images,tmp)
                else:
                    images = "%s%s" %(images,tmp)
            except:
                print "Cannot retrieve %s %s, skipping." %(data_type[0:-1],pk)
            
        images = "%s]" %(images)
    return pandas.DataFrame(json.loads(images.decode("utf-8")))

    


# Data Json Object

class DataJson:
  """DataJson: internal class for storing json, accessed by NeuroVault Object"""
  def __init__(self,url):
    self.url = url
    self.json = self.__get_json__()
    self.data = self.__parse_json__() 
    
  """Print json data fields"""
  def __str__(self):
    return "DataJson Object dj Includes <dj.data:pandas,dj.json:list,dj.url:str>"

  """Get raw json object"""
  def __get_json__(self):
    json = urllib2.urlopen(self.url).read()
    return json.decode("utf-8")
    
  """Parse a json object into a dictionary (key = fields) of dictionaries (key = file urls)"""
  def __parse_json__(self):
    if not self.json:
      self.json = self.__get_json__()
    tmp = json.loads(self.json)
    data = pandas.DataFrame(tmp)
    if data.empty: 
      print "Warning, %s is not in NeuroVault!" %(self.url)
      return None
    else: return data

  def __get_fields__(self):
    return list(self.data.columns)
