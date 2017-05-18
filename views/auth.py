"""
Auth login view: this module provides the login method
"""
from flask import abort, request
from flask_login import login_user
from flask_restful import Resource
import http.client as client

from models import User


class LoginHandler(Resource):
    """Handler of the login authentication"""

    def post(self):

        request_data = request.get_json(force=True)
        # TODO validate request data
        email = request_data['data']['attributes']['email']
        # password = request_data['data']['attributes']['password']

        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            abort(client.BAD_REQUEST)
        login_user(user)
