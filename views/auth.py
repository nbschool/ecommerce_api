"""
Auth login view: this module provides the login method
"""
from flask import abort, request
from flask_login import login_user
from flask_restful import Resource
import http.client as client

from models import User
from utils import generate_response


class LoginHandler(Resource):
    """Handler of the login authentication"""

    def post(self):
        request_data = request.get_json(force=True)
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
