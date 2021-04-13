import os
import pymongo
import bcrypt
import copy
import datetime
from bson import ObjectId
from functools import wraps

import exception
from cds.search import get_all, get_many
from crawler.crawl import crawl
from pipeline import pipeline
from datetime import datetime


class HBPService():
    def __init__(self, mongo_client):
        self.__papers = mongo_client.hbp.papers
        self.__users = mongo_client.hbp.users
        self.__updates = mongo_client.hbp.updates
        self.__feedbacks = mongo_client.hbp.feedbacks

    def __user_to_dto(self, user):
        return {
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'email': user['email'],
            'verified': user['verified'],
        }

    def read_all_papers(self):
        papers = self.__papers.find({})
        output = papers.sort('date', pymongo.DESCENDING)
        return list(output)

    def read_paper(self, id):
        paper = self.__papers.find_one({'_id': ObjectId(id)})

        if paper is None:
            raise exception.NoSuchArticleException

        return paper

    def update_paper(self, id, data):
        self.__papers.update_one(
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
            self.__papers.update_one({'_id': ObjectId(id)}, {
                '$set': {'mass_limit': data['mass_limit']}})

        if 'precision' in data:
            self.__papers.update_one({'_id': ObjectId(id)}, {
                '$set': {'precision': data['precision']}})

        return data, 200, {'Content-Type': 'application/json'}

    def delete_all_papers(self):
        return self.__papers.delete_many({})

    def delete_paper(self, id):
        result = self.__papers.delete_one({'_id': ObjectId(id)})

        if result.deleted_count == 0:
            raise exception.NoSuchArticleException

    def create_user(self, firstname, lastname, email, password):
        user_same_email = self.__users.find_one({'email': email})

        if user_same_email is not None:
            raise exception.UserAlreadyExistsException

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        user = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': password_hash,
            'verified': False
        }

        return self.__users.insert_one(user)

    def authenticate_user(self, data):
        required_fields = ['email', 'password']

        missing_fields = [
            field for field in required_fields if field not in data
        ]

        if len(missing_fields) > 0:
            raise exception.MissingFieldsException(missing_fields)

        user = self.__users.find_one({'email': data['email']})

        if user is None:
            raise exception.NoSuchUserException

        if not bcrypt.checkpw(data['password'].encode(), user['password']):
            raise exception.InvalidPasswordException

        return self.__user_to_dto(user)

    def read_user_by_email(self, email):
        user = self.__users.find_one({'email': email})

        if not user:
            raise exception.NoSuchUserException

        return self.__user_to_dto(user)

    def delete_user_by_email(self, email):
        deleted_count = self.__users.delete_one({'email': email})

        if deleted_count == 0:
            raise exception.NoSuchUserException

    def create_feedback(self, data):
        data['date'] = datetime.now()
        return self.__feedbacks.insert_one({data})

    def read_all_feedbacks(self):
        return self.__feedbacks.find({})

    def stats(self):
        count = len(list(self.__papers.find({})))
        update_history = list(self.__updates.find({}))
        return {
            'total_papers': count,
            'updates': update_history
        }

    def verification_required(self, get_identity_fn):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                email = get_identity_fn()
                user = self.__users.find_one({'email': email})

                if not user['verified']:
                    raise exception.UserNotVerifiedException
                else:
                    return fn(*args, **kwargs)
            return decorator
        return wrapper

    def connect(self):
        self.__papers.update_many(
            {}, {'$unset': {'superseded_id': '', 'supersedes_id': ''}}
        )

        superseeders = self.__papers.find(
            {'supersedes': {'$ne': None, '$exists': True}})

        for paper in superseeders:
            superseedee = self.__papers.find_one(
                {'cds_id': paper['supersedes']})
            if superseedee is not None:
                self.__papers.update_one(
                    paper, {'$set': {'supersedes_id': superseedee['_id']}}
                )

        superseeded = self.__papers.find(
            {'superseded': {'$ne': None, '$exists': True}})

        for paper in superseeded:
            superseeder = self.__papers.find_one(
                {'cds_id': paper['superseded']})
            if superseeder is not None:
                self.__papers.update_one(
                    paper, {'$set': {'superseded_id': superseeder['_id']}}
                )

    def classify(self):
        # Run NLP classifiers and recognizers on all articles in DB
        for article in list(self.__papers.find({})):
            self.classify_one(article['_id'])

    def classify_one(self, id):
        article = self.__papers.find_one({'_id': ObjectId(id)})
        classifiers = pipeline(article)

        if 'reviewed_fields' in article:
            reviewed_fields = article['reviewed_fields']
            classifiers = {key: value for key,
                           value in classifiers.items() if key not in reviewed_fields}
        else:
            classifiers['reviewed_fields'] = []

        self.__papers.update_one(article, {'$set': classifiers})

    def fill(self):
        if self.__papers.count_documents({}) > 0:
            print('Database must be empty.')
            return

        print('Filling database...')
        articles = crawl() + get_all()

        self.__papers.insert_many(articles)

        self.classify()
        self.connect()

        print('Database filled.')

    def update(self, trigger: str):
        # Search for new ATLAS and CMS papers and insert into DB (upsert)
        # Update existing ones
        print('Searching for new articles...')
        for article in get_many(['atlas_papers', 'atlas_notes', 'cms_papers', 'cms_notes']):
            self.__papers.update_one({'cds_id': article['cds_id']}, {
                '$set': article}, upsert=True)

        self.classify()
        self.connect()

        self.__updates.insert_one({
            'date': datetime.now(),
            'trigger': trigger
        })

        return 0

    def get_mass_limit(self):
        papers_with_limit = self.__papers.find(
            {'lower_limit': {'$exists': True, '$ne': None, '$gt': 0}})
        sorted_papers = papers_with_limit.sort('date', pymongo.ASCENDING)
        return list(sorted_papers)

    def get_precision(self):
        papers_with_precision = self.__papers.find(
            {'precision': {'$exists': True, '$ne': None}})
        sorted_papers = papers_with_precision.sort('date', pymongo.ASCENDING)
        return list(sorted_papers)
