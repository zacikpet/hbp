from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from commands import crawl, update
from config import db_uri


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = PyMongo(app, db_uri).db


@app.route('/papers', methods=['GET'])
@cross_origin()
def get_papers():
    papers = db.papers.find()
    output = list(papers)
    print(output)
    for item in output:
        del item['_id']
    return jsonify(output), 200, {'Content-Type': 'application/json'}


app.cli.add_command(crawl)
app.cli.add_command(update)

if __name__ == '__main__':
    app.run()
