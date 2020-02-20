"""
auth.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Authentication classes.
"""

import datetime
import jwt
from flask import request
from flask_restplus import abort
from functools import wraps


class AuthenticationToken(object):
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in

    def generate_token(self, username, role):
        info = {
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)
        }
        return jwt.encode(info, self.secret_key, algorithm='HS256')

    def validate_token(self, token):
        info = jwt.decode(token, self.secret_key, algorithms=['HS256'])
        return info


class RequiresAuth(object):
    def __init__(self, roles=None):
        self.roles = roles

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = request.headers.get('AUTH-TOKEN')
            if not token:
                abort(401, 'Authentication token is missing')
            try:
                info = auth.validate_token(token)
                # TODO: check if token has expired
                if self.roles:
                    roles = self.roles if isinstance(self.roles, list) else [self.roles]
                    if info['role'] not in roles:
                        abort(401, 'Unauthorised')

            except Exception as e:
                abort(401, e)

            return func(*args, **kwargs)
        return decorated


secret_key = 'Z7sEhmOAHZldMb0Kv5W0W8GmUKcDeXWiQfHlTZgwE38N5CcDVKvUK84Yxy8BCHsS'
expires_in = 1800
auth = AuthenticationToken(secret_key, expires_in)