import os
import pymongo
import bcrypt
import copy
import datetime
from bson import ObjectId
from functools import wraps

from cds.search import get_all, get_many
from crawler.crawl import crawl
from pipeline import pipeline
from datetime import datetime

from exception import (
    NoSuchArticleException, UserAlreadyExistsException, UserNotVerifiedException,
    InvalidPasswordException, MissingFieldsException, NoSuchUserException
)


class HBPService():
    def __init__(self, mongo):
        self._papers = mongo.hbp.papers
        self._users = mongo.hbp.users
        self._feedbacks = mongo.hbp.feedbacks
        self._updates = mongo.hbp.updates

    def user_to_dto(self, user):
        return {
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'email': user['email'],
            'verified': user['verified'],
        }

    def read_all_papers(self):

        all = self._papers.find({})
        output = all.sort('date', pymongo.DESCENDING)
        return list(output)

    def read_paper(self, id):
        paper = self._papers.find_one({'_id': ObjectId(id)})

        if paper is None:
            raise NoSuchArticleException

        return paper

    def update_paper(self, id, data):
        self._papers.update_one(
            {'_id': ObjectId(id)},
            {
                '$set': {
                    'model': data['model'],
                    'luminosity': data['luminosity'],
                    'energy': data['energy'],
                    'particles': data['particles'],
                },
                '$addToSet': {
                    'reviewed_fields': {
                        '$each': ['model', 'luminosity', 'energy', 'particles']
                    }
                }
            }
        )

        if 'mass_limit' in data:
            self._papers.update_one({'_id': ObjectId(id)}, {
                '$set': {'mass_limit': data['mass_limit']}})

        if 'precision' in data:
            self._papers.update_one({'_id': ObjectId(id)}, {
                '$set': {'precision': data['precision']}})

        return data, 200, {'Content-Type': 'application/json'}

    def delete_all_papers(self):
        return self._papers.delete_many({})

    def delete_paper(self, id):
        result = self._papers.delete_one({'_id': ObjectId(id)})

        if result.deleted_count == 0:
            raise NoSuchArticleException

    def create_user(self, firstname, lastname, email, password):
        user_same_email = self._users.find_one({'email': email})

        if user_same_email is not None:
            raise UserAlreadyExistsException

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        user = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': password_hash,
            'verified': False
        }

        return self._users.insert_one(user)

    def authenticate_user(self, data):
        required_fields = ['email', 'password']

        missing_fields = [
            field for field in required_fields if field not in data
        ]

        if len(missing_fields) > 0:
            raise MissingFieldsException(missing_fields)

        user = self._users.find_one({'email': data['email']})

        if user is None:
            raise NoSuchUserException

        if not bcrypt.checkpw(data['password'].encode(), user['password']):
            raise InvalidPasswordException

        return self.user_to_dto(user)

    def read_user_by_email(self, email):
        user = self._users.find_one({'email': email})

        if not user:
            raise NoSuchUserException

        return self.user_to_dto(user)

    def delete_user_by_email(self, email):
        deleted_count = self._users.delete_one({'email': email})

        if deleted_count == 0:
            raise NoSuchUserException

    def create_feedback(self, data):
        data['date'] = datetime.now()
        return self._feedbacks.insert_one(data)

    def read_all_feedbacks(self):
        return list(self._feedbacks.find({}))

    def stats(self):
        count = len(list(self._papers.find({})))
        update_history = list(
            self._updates.find({}).sort('date', pymongo.DESCENDING)
        )
        return {
            'total_papers': count,
            'updates': update_history
        }

    def verification_required(self, get_identity_fn):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                email = get_identity_fn()
                user = self._users.find_one({'email': email})

                if not user['verified']:
                    raise UserNotVerifiedException
                else:
                    return fn(*args, **kwargs)
            return decorator
        return wrapper

    def connect(self):
        self._papers.update_many(
            {}, {'$unset': {'superseded_id': '', 'supersedes_id': ''}}
        )

        superseeders = self._papers.find(
            {'supersedes': {'$ne': None, '$exists': True}})

        for paper in superseeders:
            superseedee = self._papers.find_one(
                {'cds_id': paper['supersedes']})
            if superseedee is not None:
                self._papers.update_one(
                    paper, {'$set': {'supersedes_id': superseedee['_id']}}
                )

        superseeded = self._papers.find(
            {'superseded': {'$ne': None, '$exists': True}})

        for paper in superseeded:
            superseeder = self._papers.find_one(
                {'cds_id': paper['superseded']})
            if superseeder is not None:
                self._papers.update_one(
                    paper, {'$set': {'superseded_id': superseeder['_id']}}
                )

    def classify(self):
        # Run NLP classifiers and recognizers on all articles in DB
        for article in list(self._papers.find({})):
            self.classify_one(article['_id'])

    def classify_one(self, id):
        article = self._papers.find_one({'_id': ObjectId(id)})
        classifiers = pipeline(article)

        if 'reviewed_fields' in article:
            reviewed_fields = article['reviewed_fields']
            classifiers = {key: value for key,
                           value in classifiers.items() if key not in reviewed_fields}
        else:
            classifiers['reviewed_fields'] = []

        self._papers.update_one(article, {'$set': classifiers})

    def fill(self):
        if self._papers.count_documents({}) > 0:
            print('Database must be empty.')
            return

        print('Filling database...')
        articles = crawl() + get_all()

        self._papers.insert_many(articles)

        self.classify()
        self.connect()

        print('Database filled.')

    def update(self, trigger: str):
        # Search for new ATLAS and CMS papers and insert into DB (upsert)
        # Update existing ones
        print('Searching for new articles...')
        for article in get_many(['atlas_papers', 'atlas_notes', 'cms_papers', 'cms_notes']):
            self._papers.update_one({'cds_id': article['cds_id']}, {
                '$set': article}, upsert=True)

        self.classify()
        self.connect()

        self._updates.insert_one({
            'date': datetime.now(),
            'trigger': trigger
        })

        return 0

    def get_mass_limit(self):
        papers_with_limit = self._papers.find(
            {'lower_limit': {'$exists': True, '$ne': None, '$gt': 0}})
        sorted_papers = papers_with_limit.sort('date', pymongo.ASCENDING)
        return list(sorted_papers)

    def get_precision(self):
        papers_with_precision = self._papers.find(
            {'precision': {'$exists': True, '$ne': None}})
        sorted_papers = papers_with_precision.sort('date', pymongo.ASCENDING)
        return list(sorted_papers)
