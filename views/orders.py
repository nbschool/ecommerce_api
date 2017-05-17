"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from http.client import (BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK,
                         UNAUTHORIZED)

from flask import abort, g, request
from flask_restful import Resource

from models import database, Address, Order, Item, User
from notifications import notify_new_order
from auth import auth
from utils import generate_response

from exceptions import InsufficientAvailabilityException


class OrdersHandler(Resource):
    """ Orders endpoint. """

    def get(self):
        """ Get all the orders."""
        data = Order.json_list(Order.get_all())
        return generate_response(data, OK)

    @auth.login_required
    def post(self):
        """ Insert a new order."""

        res = request.get_json(force=True)

        errors = Order.validate_input(res)
        if errors:
            return errors, BAD_REQUEST

        # Extract data to create the new order
        req_items = res['data']['relationships']['items']['data']
        req_address = res['data']['relationships']['delivery_address']['data']
        req_user = res['data']['relationships']['user']['data']
        
        # Check that the address exist
        try:
            user = User.get(User.uuid == req_user['id'])
        except User.DoesNotExist:
            abort(BAD_REQUEST)

        # get the user from the flask.g global object registered inside the
        # auth.py::verify() function, called by @auth.login_required decorator
        # and match it against the found user.
        # This is to prevent users from creating other users' order.
        if g.user != user and g.user.admin is False:
            return ({'message': "You can't create a new order for another user"},
                    UNAUTHORIZED)

        # Check that the items exist
        item_ids = [req_item['id'] for req_item in req_items]
        items = Item.select().where(Item.uuid << item_ids)
        if items.count() != len(req_items):
            abort(BAD_REQUEST)

        # Check that the address exist
        try:
            address = Address.get(Address.uuid == req_address['id'])
        except Address.DoesNotExist:
            abort(BAD_REQUEST)

        # Generate the dict of {<Item>: <int:quantity>} to call Order.add_items
        items_to_add = {}
        for req_item in req_items:
            item = next(i for i in items if str(i.uuid) == req_item['id'])
            items_to_add[item] = req_item['quantity']

        with database.atomic():
            try:
                order = Order.create_order(g.user, address, items_to_add)
            except InsufficientAvailabilityException:
                abort(BAD_REQUEST)

        return generate_response(order.json(), CREATED)


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_uuid):
        """ Get a specific order, including all the related Item(s)."""
        try:
            order = Order.get(Order.uuid == order_uuid)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        return generate_response(order.json(), OK)

    @auth.login_required
    def patch(self, order_uuid):
        """ Modify a specific order. """

        res = request.get_json(force=True)

        errors = Order.validate_input(res, partial=True)
        if errors:
            return errors, BAD_REQUEST

        data = res['data']['relationships']
        req_items = data.get('items')
        req_address = data.get('delivery_address')

        with database.atomic():
            try:
                order = Order.get(uuid=str(order_uuid))
            except Order.DoesNotExist:
                abort(NOT_FOUND)

            address = None
            if req_address:
                try:
                    address = Address.get(Address.uuid == req_address['data']['id'])
                except Address.DoesNotExist:
                    abort(BAD_REQUEST)
                order.delivery_address = address

            # get the user from the flask.g global object registered inside the
            # auth.py::verify() function, called by @auth.login_required decorator
            # and match it against the found user.
            # This is to prevent users from modify other users' order.
            if g.user != order.user and g.user.admin is False:
                return ({'message': "You can't delete another user's order"},
                        UNAUTHORIZED)

            # Generate the dict of {<Item>: <int:difference>} to call Order.update_items
            items_uuids = [e['id'] for e in req_items.get('data', [])]
            items = list(Item.select().where(Item.uuid << items_uuids))
            if len(items) != len(items_uuids):
                abort(BAD_REQUEST)
            items_to_add = {
                item: req_item['quantity']
                for item in items for req_item in req_items.get('data', [])
                if str(item.uuid) == req_item['id']
            }
            try:
                order.update_items(items_to_add, new_address=address)
            except InsufficientAvailabilityException:
                abort(BAD_REQUEST)

        return generate_response(order.json(), OK)

    @auth.login_required
    def delete(self, order_uuid):
        """ Delete a specific order. """
        try:
            obj = Order.get(uuid=str(order_uuid))
        except Order.DoesNotExist:
            return None, NOT_FOUND

        # get the user from the flask.g global object registered inside the
        # auth.py::verify() function, called by @auth.login_required decorator
        # and match it against the found user.
        # This is to prevent users from deleting other users' account.
        if g.user != obj.user and g.user.admin is False:
            return ({'message': "You can't delete another user's order"},
                    UNAUTHORIZED)

        obj.delete_instance(recursive=True)
        return None, NO_CONTENT
