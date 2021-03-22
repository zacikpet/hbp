import os

import pymongo
from dotenv import load_dotenv
from cds.search import get_all, get_many
from crawler.crawl import crawl
from pipeline import pipeline
from datetime import datetime

load_dotenv()
db_uri = os.getenv('DB_URI')

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers
updates: pymongo.collection.Collection = mongo.hbp.updates


def stats():
    count = len(list(papers.find({})))
    update_history = list(updates.find({}))
    return {
        'total_papers': count,
        'updates': update_history
    }


def connect():
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


def classify():
    # Run NLP classifiers and recognizers on all articles in DB
    print('Classifying articles...')
    for article in list(papers.find({})):
        classifiers = pipeline(article)
        papers.update_one(article, {'$set': classifiers})


def fill():
    if papers.count_documents({}) > 0:
        print('Database must be empty.')
        return

    print('Filling database...')
    articles = crawl() + get_all()

    papers.insert_many(articles)

    classify()
    connect()

    print('Database filled.')


def update():
    # Search for new ATLAS and CMS papers and insert into DB (upsert)
    # Update existing ones
    print('Searching for new articles...')
    for article in get_many(['atlas_papers', 'atlas_notes', 'cms_papers', 'cms_notes']):
        papers.update_one({'cds_id': article['cds_id']}, {'$set': article}, upsert=True)

    classify()
    connect()

    updates.insert_one({
        'date': datetime.now()
    })

    print('Database updated.')

    return 0


def erase():
    print('Erasing database...')
    papers.delete_many({})
    print('Database erased.')
