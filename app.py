import pymongo
from flask import Flask, abort, jsonify
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.cursor import Cursor

from commands import update, connect, erase, search
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
    paper = papers.find_one({'id': id})

    if paper is None:
        abort(404)

    return jsonify(paper), 200, {'Content-Type': 'application/json'}


@app.route('/papers', methods=['GET'])
@cross_origin()
def get_papers():
    return response(
        papers.find()
    )


app.cli.add_command(search)
app.cli.add_command(update)
app.cli.add_command(connect)
app.cli.add_command(erase)

if __name__ == '__main__':
    app.run()
