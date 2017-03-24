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

from flask import Flask
from models import database
from models import User
from flask_restful import Api
from views.user import UsersHandler
from views.user import UserHandler


app = Flask(__name__)
api = Api(app)


@app.before_request
def before_request():

    if database.is_closed():
        database.connect()

    if not User.table_exists():
        User.create_table()


@app.teardown_request
def teardown_request(response):
    if not database.is_closed():
        database.close()
    return response


api.add_resource(UsersHandler, '/api/users/')
api.add_resource(UserHandler, '/api/users/<email>')
