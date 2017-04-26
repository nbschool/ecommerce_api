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
from flask_cors import CORS

from models import database
from views.orders import OrdersHandler, OrderHandler
from views.items import ItemHandler, ItemsHandler
from views.user import UsersHandler, UserHandler

from views.address import AddressesHandler, AddressHandler
from views.pictures import PicturesHandler, PictureHandler, ItemPictureHandler

app = Flask(__name__)
CORS(app)
api = Api(app)


@app.before_request
def bad_content_type():
    """Checks for a correct request"""

    # In case of POST of a picture a "multipart/form-data" has to be specified
    # in the content-type of the request header
    if request.endpoint == 'itempicturehandler' and request.method == 'POST':
        ct = dict(request.headers).get('Content-Type', '')
        if "multipart/form-data" not in ct:
            abort(BAD_REQUEST)
    # Force POST and PUT methods to have `Content-Type` as 'application/json'
    # before proceeding inside the method handlers, that use `request.get_json`
    # from `flask.request` that require the header to be set in order to return
    # the content of the request.
    elif request.method in ('POST', 'PUT'):
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


api.add_resource(AddressesHandler, "/addresses/")
api.add_resource(AddressHandler, "/addresses/<uuid:address_id>")
api.add_resource(ItemsHandler, "/items/")
api.add_resource(ItemHandler, "/items/<uuid:item_id>")
api.add_resource(ItemPictureHandler, '/items/<uuid:item_id>/pictures/')
api.add_resource(OrdersHandler, '/orders/')
api.add_resource(OrderHandler, '/orders/<uuid:order_id>')
api.add_resource(UsersHandler, '/users/')
api.add_resource(UserHandler, '/users/<uuid:user_id>')
api.add_resource(PicturesHandler, '/pictures/')
api.add_resource(PictureHandler, '/pictures/<uuid:picture_id>')
