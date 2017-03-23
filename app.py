"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

TODO: Summarize what can be done with the api and the endpoints
"""

from flask import Flask
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from models import User, database
from http.client import BAD_REQUEST
from http.client import CREATED
from http.client import INTERNAL_SERVER_ERROR
from http.client import OK
from http.client import NOT_FOUND

app = Flask(__name__)
api = Api(app)


def non_empty_str(val, name):
    """ Custom type for reqparser, blocking empty strings. """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


def email_exists(email):
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

    if not User.table_exists():
        User.create_table()


@app.teardown_request
def teardown_request(response):
    if not database.is_closed():
        database.close()
    return response


class UsersHandler(Resource):
    """
    Handler for main user endpoint.
    Allows creation of new users and retrieval of the users list.
    """

    def get(self):
        # TODO: Add case for table missing
        return [user.get_json() for user in User.select()], OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', required=True, type=non_empty_str)
        parser.add_argument('last_name', required=True, type=non_empty_str)
        parser.add_argument('email', required=True, type=non_empty_str)
        parser.add_argument('password', required=True, type=non_empty_str)

        u_data = parser.parse_args()

        # If email is present in the database return a BAD_REQUEST response.
        if email_exists(u_data['email']):
            msg = {
                'message': 'email already present.'
            }
            return msg, BAD_REQUEST

        # Create the new user
        new_user = User.create(
            first_name=u_data['first_name'].capitalize(),
            last_name=u_data['last_name'].capitalize(),
            email=u_data['email'],
            password=u_data['password'],
        )

        # If there was an error creating the new user (None) notify the client
        if new_user is None:
            # TODO: get the exception for the creation of the new user and
            # return that.
            return None, INTERNAL_SERVER_ERROR

        # If everything went OK return the newly created user and CREATED code
        return new_user.get_json(), CREATED


class UserHandler(Resource):
    """
    Handler for the operating on a single user.
    Allows retrieving the user data, edit it and delete the user from the
    database.
    """

    def get(self, email):
        """Get a single user using the email."""
        if not email_exists(email):
            return None, NOT_FOUND

        user = User.get(User.email == email)
        return user.get_json(), OK

    def put(self, email):
        # TODO: Validate payload
        # TODO: Return BAD_REQUEST if payload not valid
        # TODO: Check user exists
        # TODO: Return NOT_FOUND if user not found
        # TODO: Update user data
        # TODO: Return (user, OK) if everything went fine
        pass

    def delete(self, email):
        # TODO: Find user => return NOT_FOUND if not found
        # TODO: Delete user from database
        # TODO: Return (NO_CONTENT, OK)
        pass


api.add_resource(UsersHandler, '/api/users/')
api.add_resource(UserHandler, '/api/user/<email>')
