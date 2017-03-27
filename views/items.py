"""
Items view: this module provides methods to interact
with items resources
"""

from models import Item as ItemModel

from flask_restful import reqparse, Resource
import http.client as client

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"


def non_emtpy_str(val, name):
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


class ItemListHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in ItemModel.select()], client.OK

    def post(self):
        """Insert a new item"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=non_emtpy_str, required=True)
        parser.add_argument('picture', type=non_emtpy_str, required=False)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('description', type=non_emtpy_str, required=True)
        args = parser.parse_args(strict=True)
        obj = ItemModel(name=args['name'],
                        price=args['price'],
                        description=args['description'])

        inserted = obj.save()
        if inserted != 1:
            return None, client.INTERNAL_SERVER_ERROR
        return obj.json(), client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, iid):
        """Retrieve the item specified by iid"""
        try:
            return ItemModel.select().where(
                ItemModel.id == iid).get().json(), client.OK
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND

    def put(self, iid):
        """Edit the item specified by iid"""
        try:
            obj = ItemModel.select().where(ItemModel.id == iid).get()
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=non_emtpy_str, required=True)
        parser.add_argument('picture', type=non_emtpy_str, required=False)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('description', type=non_emtpy_str, required=True)
        args = parser.parse_args(strict=True)

        obj.name = args['name']
        obj.price = args['price']
        obj.description = args['description']

        updated = obj.save()
        if updated != 1:
            return None, client.INTERNAL_SERVER_ERROR
        return obj.json(), client.OK

    def delete(self, iid):
        """Remove the item specified by iid"""
        try:
            obj = ItemModel.select().where(ItemModel.id == iid).get()
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
