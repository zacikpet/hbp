import click
import pymongo
from flask.cli import with_appcontext
from config import db_uri

mongo = pymongo.MongoClient(db_uri)
db = mongo.hbp


@click.command('crawl')
@click.argument('name')
@with_appcontext
def crawl(name):
    print('Crawling ' + name)
    print(db.papers.find_one())
