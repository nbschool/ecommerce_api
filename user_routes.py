"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

TODO: Summarize what can be done with the api and the endpoints
"""

from flask import Flask
from flask_restful import Resource
from flask_restful import Api
from models.user import User, database


app = Flask(__name__)
api = Api(app)


# TODO: add before_request and teardown_request decorators for database connect

class UserRoot(Resource):
    """
    Handler for main user endpoint.
    Allows creation of new users and retrieval of the users list.
    """

    def get(self):
        # TODO: Get all users
        pass

    def post(self):
        # TODO: Parse the rest arguments with reqparse
        # TODO: Create the uuid
        # TODO: Create the new user
        # TODO: Return (new_user, OK)
        pass


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


api.add_resource(UserRoot, '/user/')
api.add_resource(UserHandler, '/user/<uuid:user_id>')
