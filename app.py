from flask import Flask
from flask_restful import Api
from views.items import ItemHandler, ItemListHandler
from views.pictures import PictureHandler, PictureListHandler
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
api.add_resource(PictureListHandler, "/pictures/")
api.add_resource(PictureHandler, "/pictures/<int:picture_id>")
