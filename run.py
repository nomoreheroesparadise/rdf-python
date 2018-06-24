from flask import Flask, render_template, redirect
from pymongo import MongoClient
from classes import *
from crawler import Crawler
from pprint import pprint

# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('172.26.0.2:27017')
db = client.TaskManager
limit=10;
crawler = Crawler()


def crawlRDF(form):
    limit = form.limit.data
    type = 'rdf';
    starting_page = form.domain.data
    crawler.startWorker(starting_page, type, limit)
    return redirect('/')


def crawlJSONLD(form):
    limit = form.limit.data
    type = 'jsonld'
    starting_page = form.domain.data
    crawler.startWorker(starting_page, type, limit)
    return redirect('/')


@app.route('/', methods=['GET','POST'])
def main():
    # create form
    cform = CrawlRDFTask(prefix='cform')
    uform = CrawlJSONTask(prefix='uform')

    # response
    if cform.validate_on_submit() and cform.crawl.data:
        return crawlRDF(cform)
    if uform.validate_on_submit() and uform.crawl.data:
        return crawlJSONLD(uform)

    data = []

    return render_template('home.html', cform = cform, uform = uform, \
            data = data)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
