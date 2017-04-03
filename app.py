"""
Module contains the route handlers for the user part of the RESTful part of the
flask application.

Enpoints can be found at `/users/` and allow the creation of new users with
* `first_name`
* `last_name`
* `email`
* `password`

Fields are required non empty strings. At the current stage of development
there is no validation on what the fields contain.

User can be deleted using `/api/users/<email>` and a list of all existing users
can be retrieved making a GET to `/api/users/`
"""

from flask import abort, Flask, request
from flask_restful import Api
from http.client import BAD_REQUEST

from models import database
from views.items import ItemHandler, ItemsHandler
from views.user import UsersHandler, UserHandler

app = Flask(__name__)
api = Api(app)


@app.before_request
def bad_content_type():
    """
    Force POST and PUT methods to have `Content-Type` as 'application/json'
    before proceeding inside the method handlers, that use `request.get_json`
    from `flask.request` that require the header to be set in order to return
    the content of the request.
    """

    if request.method in ('POST', 'PUT'):
        ct = dict(request.headers).get('Content-Type', '')

        if ct != 'application/json':
            abort(BAD_REQUEST)


@app.before_request
def database_connect():
    if database.is_closed():
        database.connect()


@app.teardown_request
def database_disconnect(response):
    if not database.is_closed():
        database.close()
    return response


api.add_resource(ItemsHandler, "/items/")
api.add_resource(ItemHandler, "/items/<uuid:item_id>")
api.add_resource(UsersHandler, '/users/')
api.add_resource(UserHandler, '/users/<email>')
