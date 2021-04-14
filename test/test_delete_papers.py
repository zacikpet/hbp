import pymongo
import mongomock
from unittest import mock, TestCase
from bson import ObjectId
from exception import NoSuchArticleException

from service import HBPService


class TestReadPapers(TestCase):
    def setUp(self):
        self.mongo = mongomock.MongoClient()
        self.service = HBPService(self.mongo)

    def test_delete_paper_fail(self):

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'
        id3 = '789fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
        ]

        self.mongo.hbp.papers.insert_many(papers)

        with self.assertRaises(NoSuchArticleException):
            self.service.delete_paper(id3)

        assert self.mongo.hbp.papers.count_documents({}) == 2
        assert self.mongo.hbp.papers.find_one({'_id': ObjectId(id3)}) is None
        assert self.mongo.hbp.papers.find_one(
            {'_id': ObjectId(id2)}) is not None
        assert self.mongo.hbp.papers.find_one(
            {'_id': ObjectId(id3)}) is None

    def test_delete_paper(self):

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'
        id3 = '789fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
            {'_id': ObjectId(id3), 'title': 'Third'}
        ]

        self.mongo.hbp.papers.insert_many(papers)

        self.service.delete_paper(id1)

        assert self.mongo.hbp.papers.count_documents({}) == 2
        assert self.mongo.hbp.papers.find_one({'_id': ObjectId(id1)}) is None
        assert self.mongo.hbp.papers.find_one(
            {'_id': ObjectId(id2)}) is not None
        assert self.mongo.hbp.papers.find_one(
            {'_id': ObjectId(id3)}) is not None
