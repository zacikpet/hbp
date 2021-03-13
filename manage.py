import pymongo
from config import db_uri

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers

one_doi = papers.find({'doi': {'$size': 1}})

for paper in one_doi:
    print(paper['doi'][0])
