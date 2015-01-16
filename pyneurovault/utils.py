#!/usr/bin/env python

"""

utils: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api

"""

__author__ = ["Poldracklab (vsochat@stanford.edu)"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/15 $"
__license__ = "Python"

import os
import json
import errno
import urllib2
import numpy as np
from pandas.io.json import read_json
from urllib2 import Request, urlopen, HTTPError

# File operations 

def mkdir_p(path):
  try:
      os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

def url_get(url):
  request = Request(url)
  response = urlopen(request)
  return response.read()

# Data Json Object

class DataJson:
  """DataJson: internal class for storing json, accessed by NeuroVault Object"""
  def __init__(self,url):
    self.url = url
    self.json = self.__get_json__()
    self.data = self.__parse_json__() 
    self.fields = self.__get_fields__()

  """Print json data fields"""
  def __str__(self):
    return "DataJson Object dj Includes <dj.data:dict,js.json:list,dj.fields:list,dj.url:str>"

  """Get raw json object"""
  def __get_json__(self):
    return urllib2.urlopen(self.url).read()
    
  """Parse a json object into a dictionary (key = fields) of dictionaries (key = file urls)"""
  def __parse_json__(self):
    if not self.json:
      self.json = self.__get_json__()
    return read_json(self.json)
    
  def __get_fields__(self):
    return list(self.data.columns)
