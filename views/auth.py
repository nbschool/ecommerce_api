"""
Auth login view: this module provides the login method
"""

from flask import abort, request
from flask_cors import cross_origin
from flask_login import login_user, logout_user
from flask_restful import Resource
import http.client as client

from models import User
from utils import generate_response


class LoginHandler(Resource):
    """Handler of the login authentication"""

    @cross_origin(supports_credentials=True)
    def post(self):
        request_data = request.get_json(force=True)

        if 'email' not in request_data or 'password' not in request_data:
            abort(client.BAD_REQUEST)

        email = request_data['email']
        password = request_data['password']

        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            abort(client.BAD_REQUEST)

        if not user.verify_password(password):
            abort(client.UNAUTHORIZED)

        login_user(user)
        return generate_response({}, client.OK)


class LogoutHandler(Resource):
    """Handler to logout users. """

    def post(self):
        logout_user()
        return generate_response({}, client.OK)
