from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from w3lib.html import get_base_url
from pymongo import MongoClient
import rdflib
from time import gmtime, strftime
import extruct
import os

import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Crawler:
  def __init__(self):
    self.visitedUrls = {}
    self.toBeVisitedUrls = {}
    self.client = MongoClient(os.environ['SEMANTICWEB_MONGO_URL'])
    self.db = self.client['pyrdf']
    self.limit = 10
    self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    self.onlyDomain = True

  def startWorker(self, url, type, limit, onlyDomain):
    self.limit = limit;
    self.task(url, type)
    self.onlyDomain = bool(onlyDomain)

    for i in range(1, int(self.limit)):
      try:
        if(i == int(self.limit) -1 ):
          print('Finished crawling now: ', strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.task(next(iter(self.toBeVisitedUrls.keys())), type)
      except Exception as e:
        pass

  def task(self, url, type):
      html = self.getHTML(url)
      links = self.getLinks(url, type, html)
      if type == "rdf":
        semantic_obj = self.parseRDF(url, type)
      elif type == "jsonld":
        semantic_obj = self.parseJSONld(url,html, type)
      self.addToMongo(url, html, semantic_obj, type)


  def getHTML(self, url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = Request(url, headers=self.headers)
    html_page = urlopen(req, context=ctx)
    soup = BeautifulSoup(html_page, "lxml")
    return soup

  def getLinks(self, url, type, html):
      if(self.visitedUrls.get(url) != None):
        return None
      # Add to visitedUrls
      self.visitedUrls[url]=1
      try:
        del self.toBeVisitedUrls[url]
      except KeyError:
        pass

      soup = html
      domain = urlparse(url).netloc
      protocol = urlparse(url).scheme
      links = []
      domainCrawl = True
      if (self.onlyDomain == True):
        domainCrawl = urlparse(url).netloc == domain
      try:
        for link in soup.findAll('a'):
          if type == "rdf" and not self.hasResourcePath(link.get('href')):
            continue
          url = link.get('href')
          if url.startswith('/') and not url.startswith('//'):
            url = protocol + '://' + domain + url
          if (domainCrawl and
            self.visitedUrls.get(url) == None and
            self.toBeVisitedUrls.get(url) == None):
            links.append(url)
            self.toBeVisitedUrls[url]=1
        return links
      except Exception as e:
        pass

  def hasResourcePath(self, url):
    path = urlparse(url).path
    return path.startswith('/resource/')

  def addToMongo(self, url, html, semantic_obj, type):
    obj_to_add = {
      "url": url,
      "body": str(html),
      "object": semantic_obj,
      "type": type
    }
    semantic_objs = self.db.semantic_objs
    return semantic_objs.insert(obj_to_add, check_keys=False)


  def parseRDF(self, url, type):
    g=rdflib.Graph()
    g.load(url)
    rdfDict = {}
    iterator = 0
    for s,p,o in g:
        rdfDict[str(iterator)] = {'subject': s, 'predicate': p, 'object': o}
        iterator = iterator+1

    return rdfDict

  def parseJSONld(self, url, html, type):
    p = (html.find('script', {'type':'application/ld+json'}))
    data = p.find(text=True)
    rdfDict = {}
    iterator = 0

    g = rdflib.Graph().parse(data=data, format='json-ld')
    for s,p,o in g:
      rdfDict[str(iterator)] = {'subject': s, 'predicate': p, 'object': o}
      iterator = iterator+1

    return rdfDict


  def getToBeVisitedUrls(self):
    return self.toBeVisitedUrls

  def getVisitedUrls(self):
    return self.visitedUrls