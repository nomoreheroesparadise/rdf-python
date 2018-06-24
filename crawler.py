from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from w3lib.html import get_base_url
from pymongo import MongoClient
import rdflib
import extruct

import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Crawler:
  def __init__(self):
    self.visitedUrls = {}
    self.toBeVisitedUrls = {}
    self.client = MongoClient('mongodb://172.26.0.2:27017/')
    self.db = self.client['pyrdf']
    self.limit = 10
    self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

  def startWorker(self, url, type, limit):
    self.limit = limit;
    self.task(url, type)
    print(self.toBeVisitedUrls.keys())
    for i in range(0, self.limit):
      try:
        self.task(next(iter(self.toBeVisitedUrls.keys())), type)
      except Exception as e:
        pass

  def task(self, url, type):
      print(url,type)
      html = self.getHTML(url)
      links = self.getLinks(url, type, html)
      if type == "rdf":
        semantic_obj = self.parseRDF(url, type)
      elif type == "jsonld":
        semantic_obj = self.parseJSONld(url,html, type)
      self.addToMongo(url, html, semantic_obj, type)


  def getHTML(self, url):
     req = Request(url, headers=self.headers)
     html_page = urlopen(req)
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

      # print(self.visitedUrls)
      soup = html
      domain = urlparse(url).netloc
      protocol = urlparse(url).scheme
      links = []
      try:
        for link in soup.findAll('a'):
          if type == "rdf" and not self.hasResourcePath(link.get('href')):
            continue
          # TODO: should only have links that have proper domain
          url = link.get('href')
          if url.startswith('/') and not url.startswith('//'):
            url = protocol + '://' + domain + url
          if (urlparse(url).netloc == domain and
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
    base_url = get_base_url(str(html), url)
    data = extruct.extract(str(html), base_url)
    return data

  def getToBeVisitedUrls(self):
    return self.toBeVisitedUrls

  def getVisitedUrls(self):
    return self.visitedUrls