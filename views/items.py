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

    def put(self, item_id):
        """Edit the item specified by item_id"""
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
        """Remove the item specified by item_id"""
        """
        Delete an existing user from the database, looking up by email.
        If the email does not exists return NOT_FOUND.
        """

        if not User.exists(email):
            return ({'message': 'user `{}` without authorization to delete.'
                    .format(email)}, NOT_FOUND)

        user = User.get(User.email == email)

        # get the user from the flask.g global object registered inside the
        # auth.py::verify() function, called by @auth.login_required decorator
        # and match it against the found user.
        # This is to prevent users from deleting other users' account.
        if g.user != user:
            return ({'message': "You can't delete any item"},
                    UNAUTHORIZED)

        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
