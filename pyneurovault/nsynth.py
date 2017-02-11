#!/usr/bin/env python

'''

nsynth: functions for neurosynth integrated analysis, part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


'''

import json
import numpy as np
import pandas as pd
from pyneurovault.utils import get_url

try:
    from urllib.parse import urlencode, urlparse
    from urllib.request import urlopen, Request, unquote
    from urllib.error import HTTPError
except ImportError:
    from urllib import urlencode, unquote
    from urlparse import urlparse
    from urllib2 import urlopen, Request, HTTPError


__author__ = ["Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

# Use a joblib memory, to avoid depending on an Internet connection
from joblib import Memory
mem = Memory(cachedir='/tmp/neurovault_analysis/cache')

def get_neurosynth_terms(combined_df):
    """ Grab terms for each image, decoded with neurosynth"""
    terms = []
    scores = dict()
    for row in combined_df.iterrows():
        image_id = row[1]['image_id']
        image_url = row[1]['file']
        try:
            elevations = mem.cache(get_url)('http://neurosynth.org/api/v2/decode/?url=%s' % image_url)
            data = json.loads(elevations)['data']
            data = data['values']
            if data:
                scores[image_id] = data
                terms = np.unique(terms + data.keys()).tolist()
        except HTTPError:
            data = {}
  
    print("Preparing data frame...")
    df = pd.DataFrame(columns=["neurosynth decoding %s" %(t) for t in terms])
    for image_id,decode in scores.iteritems():
      df.loc[image_id,["neurosynth decoding %s" %(t) for t in decode.keys()]] = decode.values() 
    df["image_id"] = df.index
    return df
