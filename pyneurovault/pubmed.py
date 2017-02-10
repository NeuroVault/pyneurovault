#!/usr/bin/env python

'''

pubmed: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api


'''

from Bio import Entrez

from nltk import (
    PorterStemmer, 
    word_tokenize
)

import os
import pandas as pd
import re
import sys
import tarfile

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"

# Pubmed 
# These functions will find papers of interest to crosslist with Neurosynth
class Pubmed:

  """Init Pubmed Object"""
  def __init__(self,email):
    self.email = email

  def _get_pmc_lookup(self):
    print("Downloading latest version of pubmed central ftp lookup...")
    self.ftp = pd.read_csv("ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/file_list.txt",skiprows=1,sep="\t",header=None)
    self.ftp.columns = ["URL","JOURNAL","PMCID"]
  
  def get_pubmed_central_ids(self):
    if not self.ftp: self._get_pmc_lookup()
    return list(self.ftp["PMCID"])

  """Download full text of articles with pubmed ids pmids to folder"""
  def download_pubmed(self,pmids,download_folder):
    if not self.ftp: self._get_pmc_lookup()
    # pmids = [float(x) for x in pmids]
    # Filter ftp matrix to those ids
    # I couldn't figure out how to do this in one line
    subset = pd.DataFrame(columns=self.ftp.columns)
    for p in pmids:
      row = self.ftp.ix[self.ftp.index[self.ftp.PMCID == p]]
      subset = subset.append(row)
    # Now for each, assemble the URL 
    for row in subset.iterrows():
      url = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/%s" % (row[1]["URL"])
      print("Downloading %s" %url)
      download_place = "%s/" %(download_folder)
      if not os.path.isfile("%s%s" %(download_place,row[1]["URL"])): 
        os.system("wget \"%s\" -P %s" % (url,download_place))
        

  """Read and return single article (or search term) pubmed"""
  def get_single_article(self,id1):
    Entrez.email = self.email
    handle = Entrez.esearch(db='pubmed',term=id1,retmax=1)
    record = Entrez.read(handle)

    # If we have a match
    if "IdList" in record:
      if record["Count"] != "0":
        # Get the id and fetch the paper!
        print("Retrieving paper %s..." %id1)
        handle = Entrez.efetch(db='pubmed', id=record["IdList"][0],retmode='xml',retmax=1)
        record = Entrez.read(handle)
        record = record[0]
        article = Article(record)
        return article
      else: 
        print("No articles found for %s" %id1)

  """Compile search terms into one search, return all"""
  def get_many_articles(self,ids):

    pmids = []
    for id1 in ids:
      Entrez.email = self.email
      handle = Entrez.esearch(db='pubmed',term=id1,retmax=1)
      record = Entrez.read(handle)
      # If we have a match
      if "IdList" in record:
        if record["Count"] != "0":
          pmids.append(record["IdList"][0])

    if len(pmids) > 0: 
      # Retrieve them all!
      print("Retrieving %s papers..." % (len(pmids)))
      handle = Entrez.efetch(db='pubmed', id=pmids,retmode='xml')
      records = Entrez.read(handle)
      articles = dict()
      for record in records:
        articles[str(record["MedlineCitation"]["PMID"])] = Article(record)
      return articles
    else: 
        print("No articles found.")


  """Search article for a term of interest - no processing of expression. return 1 if found, 0 if not"""
  def search_article(self,article,term):
    text = [article.getAbstract()] + article.getMesh() + article.getKeywords()
    text = text[0].lower()
    expression = re.compile(term)
    # Search abstract for terms, return 1 if found
    found = expression.search(text)
    if found:
      return 1
    else:
      return 0

  """Search article for a term of interest - stem list of words first - return 1 if found, 0 if not"""
  def search_article_list(self,article,term):
    text = [article.getAbstract()] + article.getMesh() + article.getKeywords()
    text = text[0].lower()
    # Perform stemming of disorder terms
    words = []
    porter = PorterStemmer()
    [[words.append(str(porter.stem(t))) for t in word_tokenize(x.lower())] for x in term]
    # Get rid of general disease terms
    diseaseterms = ["disord","diseas","of","mental","impuls","control","health","specif","person","cognit","type","form","syndrom","spectrum","eat","depend","development","languag","by","endog","abus"]
    words = filter(lambda x: x not in diseaseterms, words)
    if len(words) > 0:
      # Get unique words
      words = list(set(words))
      term = "|".join([x.strip(" ").lower() for x in words])
      expression = re.compile(term)
      # Search abstract for terms, return 1 if found
      found = expression.search(text)
      if found:
        return 1
      else:
        return 0
    else:
      print("Insufficient search term for term %s" %term)
      return 0

  """Return dictionaries of dois, pmids, each with order based on author name (Last FM)"""
  def get_author_articles(self,author):
    
    print("Getting pubmed articles for author %s" %author)
    
    Entrez.email = self.email
    handle = Entrez.esearch(db='pubmed',term=author,retmax=5000)
    record = Entrez.read(handle)

    # If there are papers
    if "IdList" in record:
      if record["Count"] != "0":
        # Fetch the papers
        ids = record['IdList']
        handle = Entrez.efetch(db='pubmed', id=ids,retmode='xml',retmax=5000)
        records = Entrez.read(handle)
        # We need to save dois for database with 525, pmid for newer
        dois = dict(); pmid = dict()
        for record in records:
          authors = record["MedlineCitation"]["Article"]["AuthorList"]
          order = 1
          for p in authors:
            # If it's a collective, won't have a last name
            if "LastName" in p and "Initials" in p:
              person = p["LastName"] + " " + p["Initials"]
              if person == author:

                # Save the pmid of the paper and author order
                # it's possible to get a different number of pmids than dois
                if order == len(authors):
                  pmid[int(record["MedlineCitation"]["PMID"])] = order
                else:
                  pmid[int(record["MedlineCitation"]["PMID"])] = "PI"

                # We have to dig for the doi
                for r in record["PubmedData"]["ArticleIdList"]:
                  # Here is the doi
                  if bool(re.search("[/]",str(r))):
                    # If they are last, they are PI
                    if order == len(authors):
                      dois[str(r)] = "PI"
                    else:
                      pmid[int(record["MedlineCitation"]["PMID"])] = order
                      dois[str(r)] = order

            order = order + 1

      # If there are no papers
      else:
        print("No papers found for author %s" %author)

    # Return dois, pmids, each with author order
    print("Found %s pmids for author %s (for NeuroSynth 3000 database)." %(len(pmid),author))
    print("Found %s dois for author %s (for NeuroSynth 525 database)." %(len(dois),author))
    return (dois, pmid)


# ARTICLE ------------------------------------------------------------------------------
"""An articles object holds a pubmed article"""
class Article:

  def __init__(self,record):
    self._parseRecord(record)

  def get_pmid(self):
    pmid = [str(x) for x in self.ids if x.attributes["IdType"] == "pubmed"]
    return pmid[0] 

  def get_doi(self):
    doi = [str(x) for x in self.ids if x.attributes["IdType"] == "doi"]
    return doi[0] 

  def _parseRecord(self,record):
    if "MedlineCitation" in record:
      self.authors = record["MedlineCitation"]["Article"]["AuthorList"]
      if "MeshHeadingList" in record:
        self.mesh = record["MedlineCitation"]["MeshHeadingList"]
      else:
        self.mesh = []
      self.keywords = record["MedlineCitation"]["KeywordList"]
      self.medline = record["MedlineCitation"]["MedlineJournalInfo"]
      self.journal = record["MedlineCitation"]["Article"]["Journal"]
      self.title = record["MedlineCitation"]["Article"]["ArticleTitle"]
      self.year = record["MedlineCitation"]["Article"]["ArticleTitle"]
      if "Abstract" in record["MedlineCitation"]["Article"]:
        self.abstract = record["MedlineCitation"]["Article"]["Abstract"]
      else:
        self.abstract = ""
      self.ids = record["PubmedData"]["ArticleIdList"]

  """get Abstract text"""
  def getAbstract(self):
    if "AbstractText" in self.abstract:
      return self.abstract["AbstractText"][0]
    else:
      return ""

  """get mesh terms"""
  def getMesh(self):
    return [ str(x["DescriptorName"]).lower() for x in self.mesh]

  """get keywords"""
  def getKeywords(self):
    return self.keywords

# PARSE  ------------------------------------------------------------------------------
# General functions for parsing XML

def get_xml_tree(paper):
  if re.search("[.tar.gz]",paper):
    raw = extract_xml_compressed(paper)
  else:
    raw = read_xml(paper)
  return raw

'''Return text for xml tree element'''
def recursive_text_extract(xmltree):
  text = []
  queue = []
  article_ids = []
  for elem in reversed(list(xmltree)):
    queue.append(elem)
  
  while (len(queue) > 0):
    current = queue.pop()
    if current.text != None:
      text.append(current.text)
    if "pub-id-type" in current.keys():
      article_ids.append(current.text)
    if len(list(current)) > 0:
      for elem in reversed(list(current)):
        queue.append(elem)

  # The pubmed id is the first, so it will be last in the list
  pmid = article_ids[0]      
  return (pmid,text)

'''Read XML from compressed file'''
def extract_xml_compressed(paper): 
  tar = tarfile.open(paper, 'r:gz')
  for tar_info in tar:
    if os.path.splitext(tar_info.name)[1] == ".nxml":
      print("Extracting text from %s" %(tar_info.name))
      file_object = tar.extractfile(tar_info)
      return file_object.read().replace('\n', '')
          
'''Extract text from xml or nxml file directory'''
def read_xml(xml):
  with open (xml, "r") as myfile:
    return myfile.read().replace('\n', '')

'''Search text for list of terms, return list of match counts'''
def search_text(text,terms):
  vector = np.zeros(len(terms))
  for t in range(0,len(terms)):
    expression = re.compile("\s%s\s|\s%s\." %(terms[t],terms[t]))
    match = expression.findall(text)
    vector[t] = len(match)
  return vector
