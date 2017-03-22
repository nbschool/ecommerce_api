"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

TODO: Summarize what can be done with the api and the endpoints
"""

from flask import Flask
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from models.user import User, database
from http.client import BAD_REQUEST
from http.client import CREATED
from http.client import INTERNAL_SERVER_ERROR
from http.client import OK

app = Flask(__name__)
api = Api(app)


def non_empty_str(val, name):
    """ Custom type for reqparser, blocking empty strings. """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


def email_exits(email):
    """
    Check that an email exists in the User table.
    returns: bool
    """
    u = User.select().where(User.email == email)
    if u.exists():
        return True

    return False


@app.before_request
def before_request():
    if database.is_closed():
        database.connect()
        # TODO: create User table if not exists


@app.teardown_request
def teardown_request(response):
    if not database.is_closed():
        database.close()
    return response


class UserRoot(Resource):
    """
    Handler for main user endpoint.
    Allows creation of new users and retrieval of the users list.
    """

    def get(self):
        return [user.get_json() for user in User.select()], OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=non_empty_str)
        parser.add_argument('last_name', type=non_empty_str)
        parser.add_argument('email', required=True, type=non_empty_str)
        parser.add_argument('password', required=True, type=non_empty_str)

        u_data = parser.parse_args()

        # If email is present in the database return a BAD_REQUEST response
        # This is done automatically by peewee when trying to create the item,
        # so this may be discontinued
        if email_exits(u_data['email']):
            return None, BAD_REQUEST

        # Create the new user
        new_user = User.create(
            first_name=u_data['first_name'].capitalize(),
            last_name=u_data['last_name'].capitalize(),
            email=u_data['email'],
            password=u_data['password'],
        )

        # If there was an error creating the new user (None) notify the client
        if new_user is None:
            return None, INTERNAL_SERVER_ERROR

        # If everything went OK return the newly created user and CREATED code
        return new_user.get_json(), CREATED


class UserHandler(Resource):
    """
    Handler for the operating on a single user.
    Allows retrieving the user data, edit it and delete the user from the
    database.
    """

    def get(self, user_id):
        # TODO: Get the uuid4 from the string
        # TODO: If malformed uuid return BAD_REQUEST
        # TODO: Check that the user exists
        # TODO: Return the jsonified user object
        # TODO: If not exists return NOT_FOUND
        pass

    def put(self, user_id):
        # TODO: validate uuid
        # TODO: Validate payload
        # TODO: Return BAD_REQUEST if uuid or payload not valid
        # TODO: Check user exists
        # TODO: Return NOT_FOUND if uuid not found
        # TODO: Update user data
        # TODO: Return (user, OK) if everything went fine
        pass

    def delete(self, user_id):
        # TODO: Validate uuid
        # TODO: return BAD_REQUEST if malformed UUUID
        # TODO: Find user => return NOT_FOUND if not found
        # TODO: Delete user from database
        # TODO: Return NO_CONTENT, OK
        pass


api.add_resource(UserRoot, '/api/users/')
api.add_resource(UserHandler, '/api/user/<uuid:user_id>')
