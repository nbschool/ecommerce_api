"""
Flask Auth implementation
"""

from flask import g
from flask_httpauth import HTTPBasicAuth
from models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    """
    Verify the request to api endpoints.

    TODO: Write a proper docstring
    TODO: For delete user, verify that the request has been made by the
          owner of the User (email on request auth == User.email)
    """

    try:
        user = User.get(User.email == username)
        if user.verify_password(password):
            # if the user is found and verified, register it inside the flask.g
            # global object for further use inside the request handler
            g.user = user
            return True

    except User.DoesNotExist:
        return False
