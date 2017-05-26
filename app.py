"""
Application entry point.

Creates the Flask application and flask-restful Resources using our :mod:`views`
modules.

"""

import os
import utils # flake8: noqa

from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from auth import auth
from models import database
from views.address import AddressesHandler, AddressHandler
from views.auth import LoginHandler
from views.orders import OrdersHandler, OrderHandler
from views.items import ItemHandler, ItemsHandler
from views.user import UsersHandler, UserHandler
from views.pictures import PictureHandler, ItemPictureHandler
from views.favorites import FavoritesHandler, FavoriteHandler



app = Flask(__name__)
CORS(app)
api = Api(app)

auth.init_app(app)
app.secret_key = os.getenv(
    'SECRET_KEY',
    'development_secret_key',
)


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
api.add_resource(FavoritesHandler, '/favorites/')
api.add_resource(FavoriteHandler, '/favorites/<uuid:item_id>')
