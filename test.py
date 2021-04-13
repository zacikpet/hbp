import unittest
import mongomock
from bson import ObjectId
from service import HBPService
from exception import NoSuchArticleException


class TestReadPaper(unittest.TestCase):

    def test_read_all_papers_empty(self):
        mongo = mongomock.MongoClient()
        service = HBPService(mongo)

        all_papers = service.read_all_papers()

        assert len(all_papers) == 0

    def test_read_all_papers(self):
        mongo = mongomock.MongoClient()
        service = HBPService(mongo)

        papers = [
            {'title': 'Search for the Higgs boson'},
            {'title': 'Search for Supersymmetry'},
            {'title': 'Search for Dark matter'}
        ]

        mongo.hbp.papers.insert_many(papers)

        all_papers = service.read_all_papers()

        assert len(all_papers) == 3
        assert all_papers == papers

    def test_read_paper_none(self):
        mongo = mongomock.MongoClient()
        service = HBPService(mongo)

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'
        id3 = '789fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
        ]

        mongo.hbp.papers.insert_many(papers)

        with self.assertRaises(NoSuchArticleException):
            service.read_paper(id3)

    def test_read_paper(self):
        mongo = mongomock.MongoClient()
        service = HBPService(mongo)

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
        ]

        mongo.hbp.papers.insert_many(papers)

        paper = service.read_paper(id2)

        assert paper is not None
        assert paper == papers[1]


class TestDeletePaper(unittest.TestCase):

    def test_delete_paper(self):
        mongo = mongomock.MongoClient()
        service = HBPService(mongo)

        id1 = '123fffffffffffffffffffff'
        id2 = '456fffffffffffffffffffff'
        id3 = '789fffffffffffffffffffff'

        papers = [
            {'_id': ObjectId(id1), 'title': 'First'},
            {'_id': ObjectId(id2), 'title': 'Second'},
            {'_id': ObjectId(id3), 'title': 'Third'}
        ]

        mongo.hbp.papers.insert_many(papers)

        service.delete_paper(id1)

        assert mongo.hbp.papers.count_documents({})
        assert mongo.hbp.papers.find_one({'_id': ObjectId(id1)}) is None
        assert mongo.hbp.papers.find_one({'_id': ObjectId(id2)}) is not None
        assert mongo.hbp.papers.find_one({'_id': ObjectId(id3)}) is not None
