"""
HBP REST API
"""
from functools import wraps
from datetime import datetime, timezone, timedelta
from service import HBPService
import exception
import bcrypt
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request,
    get_jwt_identity, jwt_required, get_jwt
)
from database import mongo

api = Blueprint('api', __name__)

service = HBPService(mongo)


@ api.app_errorhandler(exception.UserNotVerifiedException)
def not_verified_handler():
    return jsonify(message='Verification is required for this action.'), 401


def required_fields(*fields):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            request_body = request.get_json()

            missing_fields = [
                field for field in fields if field not in request_body]

            if len(missing_fields) == 0:
                return fn(*args, **kwargs)
            else:
                return jsonify(message='Missing required fields.', fields=missing_fields)

        return wrapper
    return decorator


@ api.after_request
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


@ api.route('/register', methods=['POST'])
@ required_fields('email', 'password', 'firstname', 'lastname')
def register():
    try:
        data = request.get_json()
        service.create_user(**data)
        return jsonify(message='Account created.'), 201

    except exception.MissingFieldsException as e:
        return jsonify(message=f'Missing fields: {str(e)}'), 400

    except exception.UserAlreadyExistsException:
        return jsonify(message='User already exists'), 409


@ api.route('/login', methods=['POST'])
@ required_fields('email', 'password')
def login():

    try:
        data = request.get_json()
        user = service.authenticate_user(data)

        access_token = create_access_token(identity=user['email'])
        response = jsonify(message='Login Successful', user=user)
        set_access_cookies(response, access_token)

        return response, 200

    except exception.MissingFieldsException as e:
        return jsonify(message=f'Missing fields: {str(e)}'), 400

    except exception.NoSuchUserException:
        return jsonify(message='This account does not exist.'), 404

    except exception.InvalidPasswordException:
        return jsonify(message="Invalid password"), 404


@ api.route('/logout', methods=['POST'])
def logout():
    response = jsonify(message="Logout successful.")
    unset_jwt_cookies(response)
    return response


@ api.route('/users/current', methods=['GET'])
@ jwt_required()
def get_current_user():
    email = get_jwt_identity()

    try:
        user = service.read_user_by_email(email)
        return jsonify(user), 200

    except exception.NoSuchUserException:
        return jsonify(message='An account with this identity does not exist'), 404


@ api.route('/users/delete', methods=['DELETE'])
@ jwt_required()
def delete_user():
    email = get_jwt_identity()

    try:
        service.delete_user_by_email(email)
        return jsonify(message='Successfully deleted account.'), 204

    except exception.NoSuchUserException:
        return jsonify(message='Account does not exist'), 404


@ api.route('/verify-auth', methods=['GET'])
def verify_auth():
    token = verify_jwt_in_request(optional=True)

    if token:
        email = get_jwt_identity()
        try:
            user = service.read_user_by_email(email)
            return jsonify(message='Auth verified', logged_in=True, user=user)

        except exception.NoSuchUserException:
            return jsonify(message='Account does not exist'), 404

    return jsonify(message='No auth token provided.', logged_in=False, user=None)


@ api.route('/papers/<id>', methods=['GET'])
def get_paper(id):
    try:
        paper = service.read_paper(id)
        return jsonify(paper), 200

    except exception.NoSuchArticleException:
        return jsonify(message='This article does not exist'), 404


@ api.route('/papers/<id>', methods=['PATCH'])
@ jwt_required()
@ service.verification_required(get_jwt_identity)
def patch_paper(id):
    data = request.get_json()

    try:
        service.update_paper(id, data)
        return data, 200, {'Content-Type': 'application/json'}
    except:
        pass


@ api.route('/papers/<id>', methods=['DELETE'])
@ jwt_required()
@ service.verification_required(get_jwt_identity)
def delete_paper(id):
    try:
        service.delete_paper(id)
        return jsonify(message='Article deleted successfully.'), 204
    except exception.NoSuchArticleException:
        return jsonify(message='This article does not exist.'), 404


@ api.route('/papers', methods=['GET'])
def get_papers():
    papers = service.read_all_papers()
    return jsonify(papers), 200


@ api.route('/mass-limit', methods=['GET'])
def get_mass_limit():
    papers_with_limit = service.get_mass_limit()
    return jsonify(papers_with_limit), 200


@ api.route('/precision', methods=['GET'])
def get_precision():
    papers_with_precision = service.get_precision()
    return jsonify(papers_with_precision), 200


@ api.route('/stats', methods=['GET'])
@ jwt_required()
@ service.verification_required(get_jwt_identity)
def get_stats():
    stats = service.stats()
    return jsonify(stats), 200


@ api.route('/feedback', methods=['POST'])
def post_feedback():
    data = request.get_json()
    service.create_feedback(data)
    return jsonify(success=True)


@ api.route('/feedback', methods=['GET'])
@ jwt_required()
@ service.verification_required(get_jwt_identity)
def get_feedback():
    feedbacks = service.read_all_feedbacks()
    return jsonify(feedback=feedbacks)
