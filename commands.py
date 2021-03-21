import click
import pymongo
from flask.cli import with_appcontext
from scrapy.crawler import CrawlerProcess
from scrapy.signals import item_passed
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from cds.search import get_all, get_many
from crawler.hbp.spiders.cdf import CdfScraper
from crawler.hbp.spiders.d0 import D0Scraper

from config import db_uri
from typing import List

from pipeline import process_pipeline, classify_model, extract_production, delete_entities, classify_stage, \
    extract_decay_a, extract_entities, extract_luminosity, extract_decay_b, extract_decay_particles, extract_energy, \
    extract_collision

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers


def crawl() -> List:
    spiders = [D0Scraper, CdfScraper]

    results = []

    process = CrawlerProcess(get_project_settings())

    for spider in spiders:
        process.crawl(spider)

    def add_result(item):
        results.append(item)

    dispatcher.connect(add_result, signal=item_passed)

    process.start()

    return results


def classify(article):
    return process_pipeline(
        article,
        [classify_model, extract_entities, extract_luminosity, extract_energy, extract_collision,
         extract_production, extract_decay_a, extract_decay_b, extract_decay_particles,
         delete_entities, classify_stage]
    )


def process_articles():
    # Run NLP classifiers and recognizers on all articles in DB
    print('Classifying articles...')
    for article in list(papers.find({})):
        classifiers = classify(article)
        papers.update_one(article, {'$set': classifiers})

    # Connect relevant articles
    print('Connecting relevant articles...')
    relevant = papers.find({'$or': [
        {'supersedes': {'$ne': None, '$exists': True}},
        {'superseded': {'$ne': None, '$exists': True}}
    ]})

    for paper in relevant:
        supersedes = papers.find_one({'cds_id': paper['supersedes']})
        superseded = papers.find_one({'cds_id': paper['superseded']})

        papers.update_one(paper, {'$set': {
            'supersedes_id': supersedes['_id'] if supersedes is not None else None,
            'superseded_id': superseded['_id'] if superseded is not None else None,
        }})


@click.command('fill')
@with_appcontext
def fill():
    if papers.count_documents({}) > 0:
        print('Database must be empty.')
        return

    print('Filling database...')
    articles = crawl() + get_all()

    papers.insert_many(articles)

    process_articles()

    print('Database filled.')


@click.command('update')
@with_appcontext
def update():
    # Search for new ATLAS and CMS papers and insert into DB (upsert)
    # Update existing ones
    print('Searching for new articles...')
    for article in get_many(['atlas_papers', 'atlas_notes', 'cms_papers', 'cms_notes']):
        papers.update_one({'cds_id': article['cds_id']}, {'$set': article}, upsert=True)

    process_articles()

    print('Database updated.')


@click.command('erase')
@with_appcontext
def erase():
    print('Erasing database...')
    papers.delete_many({})
    print('Database erased.')
