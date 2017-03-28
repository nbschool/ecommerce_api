"""
Items view: this module provides methods to interact
with items resources
"""

from models import Item as ItemModel

from flask_restful import reqparse, Resource
import http.client as client
import utils


class ItemListHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in ItemModel.select()], client.OK

    def post(self):
        """Insert a new item"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=utils.non_emtpy_str, required=True)
        parser.add_argument('picture', type=utils.non_emtpy_str,
                            required=False)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('description', type=utils.non_emtpy_str,
                            required=True)
        args = parser.parse_args(strict=True)
        obj = ItemModel(
            name=args['name'],
            price=args['price'],
            description=args['description'])
        obj.save()
        return obj.json(), client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_id):
        """Retrieve the item specified by item_id"""
        try:
            return ItemModel.select().where(
                ItemModel.id == item_id).get().json(), client.OK
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND

    def put(self, item_id):
        """Edit the item specified by item_id"""
        try:
            obj = ItemModel.select().where(ItemModel.id == item_id).get()
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
        obj.save()

        return obj.json(), client.OK

    def delete(self, item_id):
        """Remove the item specified by item_id"""
        try:
            obj = ItemModel.select().where(ItemModel.id == item_id).get()
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
