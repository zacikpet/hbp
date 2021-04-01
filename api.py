import os
from datetime import datetime, timezone, timedelta
from functools import wraps

import bcrypt
import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request, \
    get_jwt_identity, jwt_required, get_jwt

api = Blueprint('api', __name__)

load_dotenv()
db_uri = os.getenv('DB_URI')

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers
updates: pymongo.collection.Collection = mongo.hbp.updates
users: pymongo.collection.Collection = mongo.hbp.users
feedbacks: pymongo.collection.Collection = mongo.hbp.feedbacks


@api.app_errorhandler(404)
def error_handler(error):
    return error, 404


@api.after_request
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


@api.route('/register', methods=['POST'])
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


@api.route('/login', methods=['POST'])
def login():
    if 'email' not in request.json or 'password' not in request.json:
        return jsonify(message='Missing email or password'), 400

    email = request.json['email']
    password = request.json['password']

    user = users.find_one({'email': email})

    if user:
        access_token = create_access_token(identity=email)

        if bcrypt.checkpw(password.encode(), user['password']):
            del user['password']
            response = jsonify(message="Login Successful", user=user)
            set_access_cookies(response, access_token)
            return response, 200
        else:
            return jsonify(message="Invalid password"), 404
    else:
        return jsonify(message='This user does not exist.'), 404


@api.route('/logout', methods=['POST'])
def logout():
    response = jsonify(message="Logout successful.")
    unset_jwt_cookies(response)
    return response


@api.route('/users/current', methods=['GET'])
@jwt_required()
def get_current_user():
    email = get_jwt_identity()

    user = users.find_one({'email': email})
    del user['password']

    if user:
        return jsonify(user), 200
    else:
        return jsonify(message='No current user'), 404


@api.route('/users/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    email = get_jwt_identity()
    deleted_count = users.delete_one({'email': email})

    if deleted_count == 0:
        return jsonify(message='User does not exist.'), 404
    else:
        return jsonify(message='Successfully deleted user.'), 200


@api.route('/verify-auth', methods=['GET'])
def verify_auth():
    token = verify_jwt_in_request(optional=True)
    if token:
        email = get_jwt_identity()
        user = users.find_one({'email': email})
        if user:
            del user['password']
            return jsonify(message='Auth verified', logged_in=True, user=user)

    return jsonify(message='No auth', logged_in=False, user=None)


@api.route('/papers/<id>', methods=['GET'])
def get_paper(id):
    paper = papers.find_one({'_id': ObjectId(id)})

    if paper is None:
        abort(404)

    return jsonify(paper), 200, {'Content-Type': 'application/json'}


@api.route('/papers/<id>', methods=['PATCH'])
@jwt_required()
@verification_required()
def patch_paper(id):
    data = request.json
    papers.update_one(
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
        papers.update_one({'_id': ObjectId(id)}, {'$set': {'mass_limit': data['mass_limit']}})

    if 'precision' in data:
        papers.update_one({'_id': ObjectId(id)}, {'$set': {'precision': data['precision']}})

    return data, 200, {'Content-Type': 'application/json'}


@api.route('/papers/<id>', methods=['DELETE'])
@jwt_required()
@verification_required()
def delete_paper(id):
    papers.delete_one({'_id': ObjectId(id)})
    return '', 204


@api.route('/papers', methods=['GET'])
def get_papers():
    items = papers.find()
    output = items.sort('date', pymongo.DESCENDING)
    return jsonify(output), 200, {'Content-Type': 'application/json'}


@api.route('/mass-limit', methods=['GET'])
def get_mass_limit():
    papers_with_limit = papers.find({'lower_limit': {'$exists': True, '$ne': None, '$gt': 0}})
    sorted_papers = papers_with_limit.sort('date', pymongo.ASCENDING)
    return jsonify(sorted_papers), 200, {'Content-Type': 'application/json'}


@api.route('/precision', methods=['GET'])
def get_precision():
    papers_with_precision = papers.find({'precision': {'$exists': True, '$ne': None}})
    sorted_papers = papers_with_precision.sort('date', pymongo.ASCENDING)
    return jsonify(sorted_papers), 200, {'Content-Type': 'application/json'}


@api.route('/stats', methods=['GET'])
@jwt_required()
@verification_required()
def get_stats():
    total_papers = papers.count_documents({})
    db_updates = updates.find({})
    return jsonify(total_papers=total_papers, updates=db_updates)


@api.route('/feedback', methods=['POST'])
def post_feedback():
    feedback = request.json
    date = datetime.now()
    feedbacks.insert_one({**feedback, 'date': date})
    return jsonify(success=True)


@api.route('/feedback', methods=['GET'])
@jwt_required()
@verification_required()
def get_feedback():
    feedback = feedbacks.find({})
    return jsonify(feedback=feedback)
