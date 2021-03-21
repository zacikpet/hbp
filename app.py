import pymongo
from bson import ObjectId
from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.cursor import Cursor

from commands import classify, connect, erase, search
from config import db_uri
from encoders import MongoJSONEncoder, ObjectIdConverter


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter

db: Database = PyMongo(app, db_uri).db

papers: Collection = db.papers


def response(items: Cursor):
    output = items.sort('date', pymongo.DESCENDING)
    return jsonify(output), 200, {'Content-Type': 'application/json'}


@app.route('/papers/<id>', methods=['GET'])
@cross_origin()
def get_paper(id):
    paper = papers.find_one({'_id': ObjectId(id)})

    if paper is None:
        abort(404)

    return jsonify(paper), 200, {'Content-Type': 'application/json'}


@app.route('/papers', methods=['POST'])
@cross_origin()
def post_paper():
    data = request.json
    result = papers.insert_one(data)
    return {'_id': result.inserted_id}, 201, {'Content-Type': 'application/json'}


@app.route('/papers/<id>', methods=['PATCH'])
@cross_origin()
def patch_paper(id):
    data = request.json

    papers.update_one({'_id': ObjectId(id)}, {'$set': data})

    return data, 200, {'Content-Type': 'application/json'}


@app.route('/papers/<id>', methods=['DELETE'])
def delete_paper(id):
    papers.delete_one({'_id': ObjectId(id)})
    return '', 204


@app.route('/papers', methods=['GET'])
@cross_origin()
def get_papers():
    return response(
        papers.find()
    )


@app.route('/mass-limit', methods=['GET'])
@cross_origin()
def get_mass_limit():
    papers_with_limit = papers.find({'lower_limit': {'$exists': True, '$ne': None, '$gt': 0}})
    sorted = papers_with_limit.sort('date', pymongo.ASCENDING)
    return jsonify(sorted), 200, {'Content-Type': 'application/json'}


app.cli.add_command(search)
app.cli.add_command(classify)
app.cli.add_command(connect)
app.cli.add_command(erase)

if __name__ == '__main__':
    app.run()
