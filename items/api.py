from flask import Flask
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import Resource
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import INTERNAL_SERVER_ERROR
from model import Item as ItemModel
from model import connect, close
import uuid


app = Flask(__name__)
api = Api(app)

@app.before_request
def _db_connect():
    connect()

@app.teardown_request
def _db_close(exc):
    close()


def non_emtpy_str(val, name):
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


class Item(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=non_emtpy_str, required=True)
        parser.add_argument('picture', type=non_emtpy_str, required=False)
        parser.add_argument('price', type=non_emtpy_str, required=True)
        parser.add_argument('description', type=non_emtpy_str, required=True)
        args = parser.parse_args(strict=True)
        obj = ItemModel(name=args['name'],
                        picture=uuid.uuid4(),
                        price=args['price'],
                        description=args['description'])

        inserted = obj.save()
        if inserted != 1:
            return None, INTERNAL_SERVER_ERROR
        return obj.json(), CREATED



api.add_resource(Item, "/items/")


