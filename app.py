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

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_cors import CORS

from models import database, User
from views.address import AddressesHandler, AddressHandler
from views.auth import LoginHandler
from views.orders import OrdersHandler, OrderHandler
from views.items import ItemHandler, ItemsHandler
from views.user import UsersHandler, UserHandler
from views.pictures import ItemPictureHandler, PictureHandler

app = Flask(__name__)
CORS(app)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(User.id == user_id)
    except User.DoesNotExist:
        return None


@login_manager.request_loader
def load_user_from_request(request):
    # basic auth
    if not request.authorization:
        return None
    try:
        user = User.get(User.email == request.authorization['username'])
    except User.DoesNotExist:
        return None

    if user.verify_password(request.authorization['password']):
        return user
    return None


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
api.add_resource(AddressHandler, "/addresses/<uuid:address_uuid>")
api.add_resource(LoginHandler, "/auth/login/")
api.add_resource(ItemsHandler, "/items/")
api.add_resource(ItemHandler, "/items/<uuid:item_uuid>")
api.add_resource(ItemPictureHandler, '/items/<uuid:item_uuid>/pictures/')
api.add_resource(OrdersHandler, '/orders/')
api.add_resource(OrderHandler, '/orders/<uuid:order_uuid>')
api.add_resource(UsersHandler, '/users/')
api.add_resource(UserHandler, '/users/<uuid:user_uuid>')
api.add_resource(PictureHandler, '/pictures/<uuid:picture_uuid>')
