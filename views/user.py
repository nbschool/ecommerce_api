
from flask import request
from flask_restful import Resource
from http.client import (CREATED, NO_CONTENT, OK,
                         BAD_REQUEST, CONFLICT, UNAUTHORIZED)
import uuid

from auth import auth
from models import User
from utils import generate_response
from notifications import notify_new_user


class UsersHandler(Resource):
    """
    Handler for main user endpoint.

    Implements:
    * `get` method to retrieve the list of all the users
    * `post` method to add a new user to the database.
    """
    @auth.login_required
    def get(self):
        if not auth.current_user.admin:
            return ({'message': "You can't get the list users."}, UNAUTHORIZED)

        data = User.json_list(User.select())
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
        notify_new_user(first_name=new_user.first_name,
                        last_name=new_user.last_name)

        # If everything went OK return the newly created user and CREATED code
        # TODO: Handle json() return value (data, errors) and handle errors not
        # empty
        return generate_response(new_user.json(), CREATED)

    @auth.login_required
    def patch(self):
        """Edit the current logged user"""

        request_data = request.get_json(force=True)

        errors = User.validate_input(request_data, partial=True)
        if errors:
            return errors, BAD_REQUEST

        user = auth.current_user
        data = request_data['data']['attributes']

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if email:
            user.email = email

        user.save()

        return generate_response(user.json(), OK)

    @auth.login_required
    def delete(self):
        """
        Delete the current logged user from the database.
        """
        user = auth.current_user

        user.delete_instance(recursive=True)
        return None, NO_CONTENT
