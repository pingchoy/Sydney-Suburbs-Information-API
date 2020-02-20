"""
users.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

API users.
"""
import json
import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Namespace
from flask_restplus import fields
from flask_restplus import reqparse
import binascii
import hashlib
from ..auth import AuthenticationToken, RequiresAuth

# Configure authentication
secret_key = 'Z7sEhmOAHZldMb0Kv5W0W8GmUKcDeXWiQfHlTZgwE38N5CcDVKvUK84Yxy8BCHsS'
expires_in = 600
auth = AuthenticationToken(secret_key, expires_in)
salt = b'\x02V\xfew\xc9\xaf\x18\x97U\x8d\x97\x19\x81X\xbfU\xab\xcb\x84=\x86\r{\xa2\xe6\x1cYS\xff*;M'

app = Flask(__name__)
api = Namespace('users', description="User account access for the API")

model = api.model('User', {
    'id': fields.Integer(description='The unique identifier for the user'),
    'username': fields.String(description='Unique username for this user'),
    'password': fields.String(description='Password for authentication'),
    'role': fields.String(description='User permissions role'),
})

# Retrieve the username and password from form data
credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', location="form", required=True)
credential_parser.add_argument('password', location="form", required=True)


@api.route('/token')
class Token(Resource):

    @api.response(201, 'Created token successful')
    @api.response(401, 'Authorisation failed')
    @api.doc(description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def post(self):
        """
        Create a new token using valid user credentials
        """
        args = credential_parser.parse_args()
        username = args.get('username')
        password = args.get('password')

        # Lookup user in the data frame
        user = df.loc[df['username'] == username]

        if not user.empty:
            user = user.iloc[0].to_dict()
            # Hash password (SHA-256) and compare with stored password
            password = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)).decode('utf-8')
            if user['password'] == password:
                return {"token": auth.generate_token(username, user['role']).decode('utf-8')}, 201

        return {"message": "authorisation has been refused for those credentials."}, 401


parser = reqparse.RequestParser()
parser.add_argument('role', choices=['admin', 'user'], help="Type of role for the user")
parser.add_argument('username', help="Username of the user")

create_parser = reqparse.RequestParser()
create_parser.add_argument('password', required=True, help="Password for the user", location="form")
create_parser.add_argument('role', required=True, choices=['admin', 'user'], help="Type of role for the user", location="form")
create_parser.add_argument('username', required=True, help="Username of the user", location="form")

update_parser = reqparse.RequestParser()
update_parser.add_argument('password', required=True, help="Password for the user", location="form")
update_parser.add_argument('role', choices=['admin', 'user'], help="Type of role for the user", location="form")
update_parser.add_argument('username', help="Username of the user", location="form")


@api.route('/')
class Users(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(401, 'Not authorised')
    @api.doc(description="Retrieve the list of users")
    @api.expect(parser, validate=True)
    @api.marshal_list_with(model)
    @RequiresAuth('admin')
    def get(self):
        """
        Returns a list of users
        """
        args = parser.parse_args()

        # Retrieve the query parameters
        role = args.get('role')
        username = args.get('username')

        # Make a reference to the dataset
        users_df = df

        if role:
            # Filter role
            users_df = users_df[users_df['role'] == role]

        if username:
            # Filter username
            users_df = users_df[users_df['username'] == username]

        # Convert data frame to JSON then to a dictionary
        json_str = users_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = idx
            ret.append(return_model)

        return ret

    @api.response(201, 'User created successfully')
    @api.response(400, 'Username in use')
    @api.response(401, 'Not authorised')
    @api.doc(description="Add a new user")
    @api.expect(create_parser, validate=True)
    @RequiresAuth('admin')
    def post(self):
        """
        Creates a new user
        """
        user = dict(request.form)

        # Check that the username has not already been used
        if len(df[df['username'] == user['username']]):
            return {"message": "Username {} is already in use".format(user['username'])}, 400

        # Hash the password
        user['password'] = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', user['password'].encode('utf-8'), salt, 100000)).decode('utf-8')

        for key in user:
            if key not in model.keys():
                # unexpected column
                return {"message": "Property {} is invalid".format(key)}, 400

        df.loc[df.index.max()+1] = user
        return {"message": "User {} is created".format(user['username'])}, 201


@api.route('/<int:id>')
@api.param('id', 'The id of the user')
class User(Resource):

    @api.response(200, 'Successfully retrieved user', model)
    @api.response(401, 'Not authorised')
    @api.response(404, 'User not found')
    @api.doc(description="Retrieve a user by their id")
    @api.marshal_with(model)
    @RequiresAuth('admin')
    def get(self, id):
        """
        Returns a user
        """
        if id not in df.index:
            api.abort(404, "User with id {} doesn't exist".format(id))

        user = dict(df.loc[id])
        user['id'] = id
        return user

    @api.response(200, 'Successfully deleted user')
    @api.response(401, 'Not authorised')
    @api.response(404, 'User was not found')
    @api.doc(description="Delete a user by their id")
    def delete(self, id):
        """
        Removes a user from the database
        """
        if id not in df.index:
            api.abort(404, "User with id {} doesn't exist".format(id))

        df.drop(id, inplace=True)
        return {"message": "User with id {} has been removed.".format(id)}, 200

    @api.response(200, 'Successful')
    @api.response(400, 'Username in use')
    @api.response(401, 'Not authorised')
    @api.response(404, 'User was not found')
    @api.expect(update_parser, validate=True)
    @api.doc(description="Update a user by its ID")
    @RequiresAuth('admin')
    def put(self, id):
        """
        Updates a user
        """
        if id not in df.index:
            api.abort(404, "User with id {} doesn't exist".format(id))

        # Load the form payload
        user = dict(request.form)

        # Get the user from the data frame
        df_user = dict(df.loc[id])

        # If username changed, check that it is not in use
        if 'username' in user and user['username'] != df_user['username']:
            if len(df[df['username'] == user['username']]):
                return {"message": "Username {} is already in use".format(user['username'])}, 400

        # If password has changed, hash the new password
        if 'password' in user:
            user['password'] = binascii.hexlify(
                hashlib.pbkdf2_hmac('sha256', user['password'].encode('utf-8'), salt, 100000)).decode('utf-8')

        # Ensure for unexpected columns
        for key in user:
            if key not in model.keys():
                # unexpected column
                return {"message": "Property {} is invalid".format(key)}, 400

        # Update the values
        for key in user:
            df.loc[id, key] = user[key]

        return {"message": "User with id {} has been successfully updated".format(id)}, 200


df = pd.read_csv('API/users/users.csv', index_col='id')