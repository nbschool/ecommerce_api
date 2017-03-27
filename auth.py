"""
Flask Auth implementation
"""

from flask_httpauth import HTTPBasicAuth
from passlib.hash import pbkdf2_sha256

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
        return pbkdf2_sha256.verify(password, user.password)

    except User.DoesNotExist:
        return False
