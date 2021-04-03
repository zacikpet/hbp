import os
import pymongo
from bson import ObjectId
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
    papers.update_many(
        {}, {'$unset': {'superseded_id': '', 'supersedes_id': ''}}
    )

    superseeders = papers.find({'supersedes': {'$ne': None, '$exists': True}})

    for paper in superseeders:
        superseedee = papers.find_one({'cds_id': paper['supersedes']})
        if superseedee is not None:
            papers.update_one(
                paper, {'$set': {'supersedes_id': superseedee['_id']}}
            )

    superseeded = papers.find({'superseded': {'$ne': None, '$exists': True}})

    for paper in superseeded:
        superseeder = papers.find_one({'cds_id': paper['superseded']})
        if superseeder is not None:
            papers.update_one(
                paper, {'$set': {'superseded_id': superseeder['_id']}}
            )


def classify():
    # Run NLP classifiers and recognizers on all articles in DB
    for article in list(papers.find({})):
        classify_one(article['_id'])


def classify_one(id):
    article = papers.find_one({'_id': ObjectId(id)})
    classifiers = pipeline(article)

    if 'reviewed_fields' in article:
        reviewed_fields = article['reviewed_fields']
        classifiers = {key: value for key,
                       value in classifiers.items() if key not in reviewed_fields}
    else:
        classifiers['reviewed_fields'] = []

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


def update(trigger: str):
    # Search for new ATLAS and CMS papers and insert into DB (upsert)
    # Update existing ones
    print('Searching for new articles...')
    for article in get_many(['atlas_papers', 'atlas_notes', 'cms_papers', 'cms_notes']):
        papers.update_one({'cds_id': article['cds_id']}, {
                          '$set': article}, upsert=True)

    classify()
    connect()

    updates.insert_one({
        'date': datetime.now(),
        'trigger': trigger
    })

    return 0


def erase():
    print('Erasing database...')
    papers.delete_many({})
    print('Database erased.')
