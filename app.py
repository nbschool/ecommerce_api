from flask import Flask
from flask_restful import Api
from views.items import ItemHandler, ItemListHandler
from models import connect, close


app = Flask(__name__)
api = Api(app)


@app.before_request
def _db_connect():
    connect()


@app.teardown_request
def _db_close(exc):
    close()


api.add_resource(ItemListHandler, "/items/")
api.add_resource(ItemHandler, "/items/<int:iid>")
