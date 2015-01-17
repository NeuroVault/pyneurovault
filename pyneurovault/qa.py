#!/usr/bin/env python

"""

qa: quality analysis and data checking functions, part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api

"""

import pandas as pd

def get_datatypes(data_frame):
  """Get data type of each column in image or collections data frame"""
  return data_frame.apply(lambda x: pd.lib.infer_dtype(x.values))
