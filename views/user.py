from flask import request
from flask import abort
from flask_restful import Resource
from models import User
from http.client import BAD_REQUEST
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
import utils


class UsersHandler(Resource):
    """
    Handler for main user endpoint.

    Implements:
    * `get` method to retrieve the list of all the users
    * `post` method to add a new user to the database.
    """

    def get(self):
        return [user.json() for user in User.select()], OK

    def post(self):
        """ Add an user to the database."""
        # required fields for an User. All fields must be inside the post
        # request and not be empty strings.
        required_fields = ['first_name', 'last_name', 'email', 'password']

        request_data = request.get_json()

        # For every field required for creating a new user trry to get the
        # value from `request.form`. If the field is missing (KeyError) or
        # the value is an empty string (ValueError) return a BAD_REQUEST
        for field in required_fields:
            try:
                value = request_data[field]
                utils.non_empty_str(value, field)
            except (KeyError, ValueError):
                abort(BAD_REQUEST)

        # If email is present in the database return a BAD_REQUEST response.
        if User.exists(request_data['email']):
            msg = {'message': 'email already present.'}
            return msg, BAD_REQUEST

        new_user = User.create(
            first_name=request_data['first_name'].capitalize(),
            last_name=request_data['last_name'].capitalize(),
            email=request_data['email'],
            password=request_data['password']
        )

        # If everything went OK return the newly created user and CREATED code
        return new_user.json(), CREATED


class UserHandler(Resource):
    """
    Handler for the operating on a single user.

    Implements:
    * `delete` method to remove an existing user from the database.
    """

    def delete(self, email):
        """
        Delete an existing user from the database, looking up by email.
        If the email does not exists return NOT_FOUND.
        """
        if not User.exists(email):
            return None, NOT_FOUND

        user = User.get(User.email == email)

        user.delete_instance()
        return None, NO_CONTENT
