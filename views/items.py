"""
Items view: this module provides methods to interact
with items resources
"""

import uuid

from flask import request
from flask_restful import Resource
import http.client as client

from models import Item


class ItemsHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in Item.select()], client.OK

    def post(self):
        """
        Insert a new item, the item_uuid identifier is forwarded
        from the one generated from the database
        """
        request_data = request.get_json(force=True)

        isValid, errors = Item.validate_input(request_data)
        if not isValid:
            return errors, client.BAD_REQUEST

        data = request_data['data']['attributes']

        if int(data['availability']) < 0:
            return None, client.BAD_REQUEST

        item = Item.create(
            uuid=uuid.uuid4(),
            name=data['name'],
            price=float(data['price']),
            description=data['description'],
            availability=int(data['availability']),
        )

        return item.json(), client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_uuid):
        """Retrieve the item specified by item_uuid"""
        try:
            return Item.get(Item.uuid == item_uuid).json(), client.OK
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

    def patch(self, item_uuid):
        """Edit the item specified by item_uuid"""
        try:
            obj = Item.get(Item.uuid == item_uuid)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json(force=True)
        name = request_data.get('name')
        price = request_data.get('price')
        description = request_data.get('description')
        availability = request_data.get('availability')

        if name and name != obj.name:
            obj.name = request_data['name']

        if price and price != obj.price:
            obj.price = request_data['price']

        if description and description != obj.description:
            obj.description = request_data['description']

        if availability and availability != obj.availability:
            obj.availability = request_data['availability']

        obj.save()

        return obj.json(), client.OK

    def delete(self, item_uuid):
        """Remove the item specified by item_uuid"""
        try:
            item = Item.get(Item.uuid == item_uuid)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        item.delete_instance()
        return None, client.NO_CONTENT
