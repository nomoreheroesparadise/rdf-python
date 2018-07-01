from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField

class CrawlRDFTask(FlaskForm):
    domain = TextField('Starting Webiste')
    limit = TextField('Limit')
    onlyDomain = TextField('onlyDomain')
    crawl = SubmitField('Crawl')

class CrawlJSONTask(FlaskForm):
    domain = TextField('Starting Webiste')
    limit = TextField('Limit')
    onlyDomain = TextField('onlyDomain')
    crawl = SubmitField('Crawl')