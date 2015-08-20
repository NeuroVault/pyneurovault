#!/usr/bin/env python

"""

utils: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api

"""

import os
import json
import errno
import pandas
from urllib2 import Request, urlopen, HTTPError

__author__ = ["Poldracklab", "Chris Filo Gorgolewski",
              "Gael Varoquaux", "Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

CWD = os.path.abspath(os.path.split(__file__)[0])


# Get standard brains
def get_standard_brain():
    return os.path.join(CWD, 'data', 'MNI152_T1_2mm_brain.nii.gz')


def get_standard_mask():
    return os.path.join(CWD, 'data', 'MNI152_T1_2mm_brain_mask.nii.gz')


# File operations
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_url(url):
    request = Request(url)
    response = urlopen(request)
    return response.read()

# From nipy Split a filename into parts: path, base filename and extension
def split_filename(fname):
    special_extensions = [".nii.gz", ".tar.gz"]

    pth = os.path.dirname(fname)
    fname = os.path.basename(fname)

    ext = None
    for special_ext in special_extensions:
        ext_len = len(special_ext)
        if (len(fname) > ext_len) and \
                (fname[-ext_len:].lower() == special_ext.lower()):
            ext = fname[-ext_len:]
            fname = fname[:-ext_len]
            break
    if not ext:
        fname, ext = os.path.splitext(fname)

    return pth, fname, ext

def get_json(url):
    '''Return general json'''
    json_single = get_url(url)
    json_single = json.loads(json_single.decode("utf-8"))
    if "count" in json_single.keys():
        if json_single["count"] == 1:
            return json_single["results"]
        else:
            print "Found %s results." % json_single["count"]
            json_all = json_single["results"]
            while json_single["next"] is not None:
                print "Retrieving %s" % json_single["next"]
                try:
                    json_single = get_url(json_single["next"])
                    json_single = json.loads(json_single.decode("utf-8"))
                    json_all = json_all + json_single['results']
                except HTTPError:
                    print "Cannot get, retrying"
            return json_all
    else:
        return json_single


def get_json_df(data_type, pks=None, limit=1000):
    '''Return paginated json data frame, for images and collections'''
    json_all = list()
    if pks is None:  # May not be feasible call if database is too big
        url = "http://neurovault.org/api/%s/?limit=%s&format=json" % (
            data_type, limit)
        json_all = pandas.DataFrame(get_json(url))

    else:
        if isinstance(pks, str):
            pks = [pks]
        elif isinstance(pks, int):
            pks = [pks]
        json_all = "["
        for p in range(0, len(pks)):
            pk = pks[p]
            print "Retrieving %s %s..." % (data_type[0:-1], pk)
            try:
                tmp = get_url("http://neurovault.org/api"
                              "/%s/%s/?format=json" %(data_type,pk))
                if p != 0:
                    json_all = "%s,%s" % (json_all, tmp)
                else:
                    json_all = "%s%s" % (json_all, tmp)
            except:
                print "Cannot retrieve %s %s, skipping." % (
                    data_type[0:-1], pk)

        json_all = "%s]" % json_all
        json_all = pandas.DataFrame(json.loads(json_all.decode("utf-8")))
    return json_all
