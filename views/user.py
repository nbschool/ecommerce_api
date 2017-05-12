
from flask import request, abort, g
from flask_restful import Resource
from http.client import (CREATED, NO_CONTENT, NOT_FOUND, OK,
                         BAD_REQUEST, CONFLICT, UNAUTHORIZED)
from flask import render_template
import uuid
from http.client import (BAD_REQUEST, CONFLICT, CREATED, NO_CONTENT, NOT_FOUND,
                         OK, UNAUTHORIZED)

from flask import g, request
from flask_restful import Resource

from auth import auth
from models import User
from utils import generate_response
from notifications import send_email
from utils import non_empty_str


class UsersHandler(Resource):
    """
    Handler for main user endpoint.

    Implements:
    * `get` method to retrieve the list of all the users
    * `post` method to add a new user to the database.
    """

    def get(self):
        data = User.json_list(User.get_all())
        return generate_response(data, OK)

    def post(self):
        """ Add an user to the database."""
        data = request.get_json(force=True)

        errors = User.validate_input(data)
        if errors:
            return errors, BAD_REQUEST

        # Extract the user attributes to check and generate the User row
        data = data['data']['attributes']

        # If email is present in the database return a BAD_REQUEST response.
        if User.exists(data['email']):
            msg = {'message': 'email already present.'}
            return msg, CONFLICT

        new_user = User.create(
            uuid=uuid.uuid4(),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=User.hash_password(data['password'])
        )
        body = render_template('new_user.html',
                               first_name=new_user.first_name,
                               last_name=new_user.last_name)

        send_email("Nuovo Utente", body)
        # If everything went OK return the newly created user and CREATED code
        # TODO: Handle json() return value (data, errors) and handle errors not
        # empty
        return generate_response(new_user.json(), CREATED)


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
