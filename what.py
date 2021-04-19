import os
import dotenv
import pymongo
import json
import random

dotenv.load_dotenv()

db_uri = os.getenv('DB_URI')

mongo = pymongo.MongoClient(db_uri)

articles = list(mongo.hbp.papers.find({}))

random.shuffle(articles)

print(articles[0])

i = 1
for a in articles:
    del a['date']
    del a['_id']
    if 'supersedes_id' in a:
        del a['supersedes_id']
    if 'superseded_id' in a:
        del a['superseded_id']
    a['number'] = i
    i += 1

with open('test_ner.json', 'w') as out:
    json.dump(articles[0:100], out)
