import os
from datetime import timedelta, datetime, timezone
from functools import wraps
import bcrypt
import pymongo
from bson import ObjectId
from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt, \
    set_access_cookies, unset_jwt_cookies
from commands import connect_command, fill_command, update_command, erase_command, classify_command, stats_command
from encoders import MongoJSONEncoder, ObjectIdConverter

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter

load_dotenv()
db_uri = os.getenv('DB_URI')
db: Database = PyMongo(app, db_uri).db

papers: Collection = db.papers
users: Collection = db.users


@app.after_request
def refresh_expiring_jwt(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=15))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


def verification_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            email = get_jwt_identity()
            user = users.find_one({'email': email})

            if not user['verified']:
                return jsonify(message='Your account is not yet verified', code='not-verified'), 401
            else:
                return fn(*args, **kwargs)

        return decorator

    return wrapper


@app.route('/register', methods=['POST'])
def register():
    if 'email' not in request.json or 'password' not in request.json:
        return jsonify(message='Missing email or password'), 400

    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']

    if users.find_one({'email': email}):
        return jsonify(message='User already exists'), 409
    else:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        user = dict(firstname=firstname, lastname=lastname, email=email, password=password_hash, verified=False)
        users.insert_one(user)
        return jsonify(message='Account created.'), 201


@app.route('/login', methods=['POST'])
def login():
    if 'email' not in request.json or 'password' not in request.json:
        return jsonify(message='Missing email or password'), 400

    email = request.json['email']
    password = request.json['password']

    user = users.find_one({'email': email})

    if user:
        access_token = create_access_token(identity=email)

        if bcrypt.hashpw(password.encode(), user['password']) == user['password']:
            response = jsonify(message="Login Successful", access_token=access_token)
            set_access_cookies(response, access_token)
            return response, 200
        else:
            return jsonify(message="Invalid password"), 404
    else:
        return jsonify(message='This user does not exist.'), 404


@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify(message="Logout successful.")
    unset_jwt_cookies(response)
    return response


@app.route('/users/current', methods=['GET'])
@jwt_required()
def get_current_user():
    email = get_jwt_identity()

    user = users.find_one({'email': email})
    del user['password']

    if user:
        return jsonify(user), 200
    else:
        return jsonify(message='No current user'), 404


@app.route('/users/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    email = get_jwt_identity()
    user = users.find_one({'email': email})

    if not user['verified']:
        return jsonify(message='Your account is not yet verified'), 401

    deleted_count = users.delete_one({'_id': ObjectId(id)})

    if deleted_count == 0:
        return jsonify(message='User does not exist.'), 404
    else:
        return jsonify(message='Successfully deleted user.'), 200


@app.route('/papers/<id>', methods=['GET'])
@cross_origin()
def get_paper(id):
    paper = papers.find_one({'_id': ObjectId(id)})

    if paper is None:
        abort(404)

    return jsonify(paper), 200, {'Content-Type': 'application/json'}


@app.route('/papers/<id>', methods=['PATCH'])
@cross_origin()
@jwt_required()
@verification_required()
def patch_paper(id):
    data = request.json

    papers.update_one({'_id': ObjectId(id)}, {'$set': data})

    return data, 200, {'Content-Type': 'application/json'}


@app.route('/papers/<id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
@verification_required()
def delete_paper(id):
    papers.delete_one({'_id': ObjectId(id)})
    return '', 204


@app.route('/papers', methods=['GET'])
@cross_origin()
def get_papers():
    items = papers.find()
    output = items.sort('date', pymongo.DESCENDING)
    return jsonify(output), 200, {'Content-Type': 'application/json'}


@app.route('/mass-limit', methods=['GET'])
@cross_origin()
def get_mass_limit():
    papers_with_limit = papers.find({'lower_limit': {'$exists': True, '$ne': None, '$gt': 0}})
    sorted_papers = papers_with_limit.sort('date', pymongo.ASCENDING)
    return jsonify(sorted_papers), 200, {'Content-Type': 'application/json'}


app.cli.add_command(fill_command)
app.cli.add_command(update_command)
app.cli.add_command(erase_command)
app.cli.add_command(classify_command)
app.cli.add_command(stats_command)
app.cli.add_command(connect_command)

if __name__ == '__main__':
    app.run()
