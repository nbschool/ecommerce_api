"""
Flask Auth implementation
"""

from flask_httpauth import HTTPBasicAuth
from models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    """
    Verify the request to api endpoints.
    TODO: Write a proper docstring
    """
    try:
        # TODO: email will change with an username field
        user = User.get(User.email == username)
        # TODO: Use passlib to verify the password
        # TODO: store the hashed password in the users
        return user.password == password
    except User.DoesNotExist:
        return False
