from flask import Flask, jsonify
from flask_pymongo import PyMongo
from commands import crawl
from config import db_uri


app = Flask(__name__)
mongo = PyMongo(app, db_uri)


@app.route('/papers', methods=['GET'])
def get_papers():
    papers = mongo.db.papers.find()
    output = [{'title': paper['title']} for paper in papers]
    return jsonify(output)


app.cli.add_command(crawl)

if __name__ == '__main__':
    app.run()
