import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
db_uri = os.getenv('DB_URI')

mongo = pymongo.MongoClient(db_uri)
