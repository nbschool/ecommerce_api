"""
Items view: this module provides methods to interact
with items resources
"""

import uuid

from flask import request
from flask_restful import Resource
import http.client as client

from models import Item
from utils import check_required_fields


class ItemsHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in Item.select()], client.OK

    def post(self):
        """
        Insert a new item, the item_id identifier is forwarded
        from the one generated from the database
        """
        request_data = request.get_json()
        check_required_fields(
            request_data=request_data,
            required_fields=['name', 'price', 'description'])

        obj = Item.create(
            item_id=uuid.uuid4(),
            name=request_data['name'],
            price=float(request_data['price']),
            description=request_data['description'])
        item = obj.json()

        return item, client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_id):
        """Retrieve the item specified by item_id"""
        try:
            return Item.get(Item.item_id == item_id).json(), client.OK
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

    def patch(self, item_id):
        """Edit the item specified by item_id"""
        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json()
        name = request_data.get('name')
        price = request_data.get('price')
        description = request_data.get('description')

        if name and name != obj.name:
            obj.name = request_data['name']

        if price and price != obj.price:
            obj.price = request_data['price']

        if description and description != obj.description:
            obj.description = request_data['description']

        obj.save()

        return obj.json(), client.OK

    def delete(self, item_id):
        """Remove the item specified by item_id"""
        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
