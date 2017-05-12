from flask import request, abort, g
from flask_restful import Resource
from http.client import (CREATED, NO_CONTENT, NOT_FOUND, OK,
                         BAD_REQUEST, CONFLICT, UNAUTHORIZED)
import uuid

from auth import auth
from models import User
from utils import non_empty_str


class UsersHandler(Resource):
    """
    Handler for main user endpoint.

    Implements:
    * `get` method to retrieve the list of all the users
    * `post` method to add a new user to the database.
    """
    @auth.login_required
    def get(self):
        if g.user.admin:
            return [user.json() for user in User.select()], OK
        return ({'message': "You can't get the list users."},
                UNAUTHORIZED)

    def post(self):
        """ Add an user to the database."""
        # required fields for an User. All fields must be inside the post
        # request and not be empty strings.
        required_fields = ['first_name', 'last_name', 'email', 'password']

        request_data = request.get_json(force=True)

        # For every field required for creating a new user try to get the
        # value from the json data of the request.
        # If the field is missing (KeyError) or the value is an empty
        # string (ValueError) return a BAD_REQUEST
        for field in required_fields:
            try:
                value = request_data[field]
                non_empty_str(value, field)
            except (KeyError, ValueError):
                abort(BAD_REQUEST)

        # If email is present in the database return a BAD_REQUEST response.
        if User.exists(request_data['email']):
            msg = {'message': 'email already present.'}
            return msg, CONFLICT

        new_user = User.create(
            uuid=uuid.uuid4(),
            first_name=request_data['first_name'],
            last_name=request_data['last_name'],
            email=request_data['email'],
            password=User.hash_password(request_data['password'])
        )

        # If everything went OK return the newly created user and CREATED code
        return new_user.json(), CREATED


class UserHandler(Resource):
    """
    Handler for the operating on a single user.

    Implements:
    * `delete` method to remove an existing user from the database.
    """

    @auth.login_required
    def delete(self, user_uuid):
        """
        Delete an existing user from the database, looking up by user_uuid.
        If the user_uuid does not exists return NOT_FOUND.
        """
        try:
            user = User.get(User.uuid == user_uuid)
        except User.DoesNotExist:
            return ({'message': 'user `{}` not found'.format(user_uuid)},
                    NOT_FOUND)

        # get the user from the flask.g global object registered inside the
        # auth.py::verify() function, called by @auth.login_required decorator
        # and match it against the found user.
        # This is to prevent users from deleting other users' account.
        if g.user != user:
            return ({'message': "You can't delete another user's account"},
                    UNAUTHORIZED)

        user.delete_instance(recursive=True)
        return None, NO_CONTENT
