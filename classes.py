from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField

class CrawlRDFTask(FlaskForm):
    domain = TextField('Starting Webiste')
    limit = TextField('Limit')
    crawl = SubmitField('Crawl')

class CrawlJSONTask(FlaskForm):
    domain = TextField('Starting Webiste')
    limit = TextField('Limit')
    crawl = SubmitField('Crawl')