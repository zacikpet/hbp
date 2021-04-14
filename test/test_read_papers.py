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

    def test_read_all_papers(self):
        new = [
            {'title': 'Search for the Higgs boson'},
            {'title': 'Search for Supersymmetry'},
            {'title': 'Search for Dark matter'}
        ]

        self.mongo.hbp.papers.insert_many(new)

        all_papers = self.service.read_all_papers()

        assert len(all_papers) == 3
        assert all_papers == new

    def test_read_all_papers_empty(self):
        all_papers = self.service.read_all_papers()

        assert len(all_papers) == 0

    def test_read_paper_fail(self):
        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'
        id3 = '789fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
        ]

        self.mongo.hbp.papers.insert_many(papers)

        with self.assertRaises(NoSuchArticleException):
            self.service.read_paper(id3)

    def test_read_paper(self):

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
        ]

        self.mongo.hbp.papers.insert_many(papers)

        paper = self.service.read_paper(id2)

        assert paper is not None
        assert paper == papers[1]
