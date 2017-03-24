"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

Enpoints can be found at `/api/users/` and allow the creation of new users with
* `first_name`
* `last_name`
* `email`
* `password`

Fields are required non empty strings. At the current stage of development there
is no validation on what the fields contain.

User can be deleted using `/api/users/<email>` and a list of all existing users
can be retrieved making a GET to `/api/users/`
"""

from flask import abort
from flask import Flask
from flask import request
from models import database
from models import User
from flask_restful import Api
from views.user import UsersHandler
from views.user import UserHandler
from http.client import BAD_REQUEST

app = Flask(__name__)
api = Api(app)


@app.before_request
def bad_content_type():
    """
    Force POST and PUT methods to have `Content-Type` as 'application/json'
    before proceeding inside the method handlers.
    """

    if request.method in ('POST', 'PUT'):
        # get the content-type for the request
        ct = dict(request.headers).get('Content-Type', '')

        # if not app/json block and return bad request.
        if ct != 'application/json':
            abort(BAD_REQUEST)


@app.before_request
def database_connect():
    if database.is_closed():
        database.connect()

    if not User.table_exists():
        User.create_table()


@app.teardown_request
def database_disconnect(response):
    if not database.is_closed():
        database.close()
    return response


api.add_resource(UsersHandler, '/api/users/')
api.add_resource(UserHandler, '/api/users/<email>')
