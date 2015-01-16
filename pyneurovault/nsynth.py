#!/usr/bin/env python

"""

nsynth: functions for neurosynth integrated analysis, part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


"""

import json
import pandas as pd
from utils import url_get
from urllib2 import Request, urlopen, HTTPError

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

# Use a joblib memory, to avoid depending on an Internet connection
from joblib import Memory
mem = Memory(cachedir='/tmp/neurovault_analysis/cache')

def get_neurosynth_terms(combined_df):
  """ Grab terms for each image, decoded with neurosynth"""
  terms = list()
  from sklearn.feature_extraction import DictVectorizer
  vectorizer = DictVectorizer()
  image_ids = list()
  for row in combined_df.iterrows():
    image_id = row[1]['image_id']
    image_ids.append(int(image_id))
    print "Fetching terms for image %i" % image_id
    image_url = row[1]['url_image'].split('/')[-2]

    try:
        elevations = mem.cache(url_get)('http://beta.neurosynth.org/decode/data/?neurovault=%s' % image_url)
        data = json.loads(elevations)['data']
        data = dict([(i['feature'], i['r']) for i in data])
    except HTTPError:
        data = {}
    terms.append(data)
  X = vectorizer.fit_transform(terms).toarray()
  term_dframe = dict([('neurosynth decoding %s' % name, X[:, idx]) for name, idx in vectorizer.vocabulary_.items()])
  term_dframe['image_id'] = image_ids
  return pd.DataFrame(term_dframe)

