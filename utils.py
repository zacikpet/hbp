from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity


def verification_required(users):
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
