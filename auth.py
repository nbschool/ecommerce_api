"""
Flask Auth implementation
"""

from flask import g
from flask_httpauth import HTTPBasicAuth
from models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify(email, password):
    """
    Verify the request to api users endpoints, trying to get the user with the
    provided email and verifying the password against the stored hashed one.

    If the user is verified it will be stored inside `Flask.g` to be used from
    the enpoint handler if needed, for example to allow `delete` or `put` only
    on the user's own account.
    """

    try:
        user = User.get(User.email == email)
        if user.verify_password(password):
            # if the user is found and verified, register it inside the flask.g
            # global object for further use inside the request handler
            g.user = user
            return True

    except User.DoesNotExist:
        return False
