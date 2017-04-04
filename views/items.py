"""
Items view: this module provides methods to interact
with items resources
"""

import uuid

from flask import request, g
from flask_restful import Resource
import http.client as client

from models import Item, User
from utils import check_required_fields
from auth import auth


class ItemsHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in Item.select()], client.OK

    @auth.login_required
    def post(self):
        """
        Insert a new item only if the pair email/password
        is validated by Authorization. 
        The item_id identifier is forwarded
        from the one generated from the database
        """
        request_data = request.get_json()
        check_required_fields(
            request_data=request_data,
            required_fields=['name', 'price', 'description'])

        obj = Item.create(
            item_id=str(uuid.uuid4()),
            name=request_data['name'],
            price=float(request_data['price']),
            description=request_data['description'])
        item = obj.json()
        item.update({'item_id': obj.id})
        return item, client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_id):
        """Retrieve the item specified by item_id"""
        try:
            return Item.get(Item.item_id == item_id).json(), client.OK
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

    @auth.login_required
    def put(self, item_id):
        """
        Edit the item specified by item_id only 
        if the pair email/password is validated by
        Authorization.
        """
        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json()
        check_required_fields(
            request_data=request_data,
            required_fields=['name', 'price', 'description'])

        obj.name = request_data['name']
        obj.price = request_data['price']
        obj.description = request_data['description']
        obj.save()

        return obj.json(), client.OK

    @auth.login_required
    def delete(self, item_id):
        """
        Remove the item specified by item_id
        only if the pair email/password
        is validated by Authorization.
        """
        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
