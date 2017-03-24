"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

Enpoints can be found at `/api/users/` and allow the creation of new users with
* `first_name`
* `last_name`
* `email`
* `password`

Fields are required non empty strings. At the current stage of development there
is no validation on what the fields contain.

User can be deleted using `/api/users/<email>` and a list of all existing users
can be retrieved making a GET to `/api/users/`
"""

from flask import Flask
from flask import request
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from models import User, database
from http.client import BAD_REQUEST
from http.client import CREATED
from http.client import INTERNAL_SERVER_ERROR
from http.client import OK
from http.client import NOT_FOUND
from http.client import NO_CONTENT

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
        return [user.get_json() for user in User.select()], OK

    def post(self):
        """ Add an user to the database."""
        # required fields for an User. All fields must be inside the post
        # request and not be empty strings.
        required_fields = ['first_name', 'last_name', 'email', 'password']

        # For every field required for creating a new user trry to get the
        # value from `request.form`. If the field is missing (KeyError) or
        # the value is an empty string (ValueError) return a BAD_REQUEST
        for field in required_fields:
            try:
                value = request.form[field]
                non_empty_str(value, field)
            except KeyError:
                return None, BAD_REQUEST
            except ValueError:
                return None, BAD_REQUEST

        # If email is present in the database return a BAD_REQUEST response.
        if email_exists(request.form['email']):
            msg = {'message': 'email already present.'}
            return msg, BAD_REQUEST

        # Create the new user
        new_user = User.create(
            first_name=request.form['first_name'].capitalize(),
            last_name=request.form['last_name'].capitalize(),
            email=request.form['email'],
            password=request.form['password']
        )

        # If everything went OK return the newly created user and CREATED code
        return new_user.get_json(), CREATED


class UserHandler(Resource):
    """
    Handler for the operating on a single user.
    Allows retrieving the user data, edit it and delete the user from the
    database.
    """

    def delete(self, email):
        """
        Delete an existing user from the database, looking up by email.
        If the email does not exists return NOT_FOUND.
        """
        if not email_exists(email):
            return None, NOT_FOUND

        user = User.get(User.email == email)

        if user:
            user.delete_instance()
            return None, NO_CONTENT


api.add_resource(UsersHandler, '/api/users/')
api.add_resource(UserHandler, '/api/users/<email>')
