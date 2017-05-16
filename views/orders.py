"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from flask_restful import Resource
from models import database, Address, Order, Item
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST, UNAUTHORIZED
from flask import abort, request, g
from auth import auth

from exceptions import InsufficientAvailabilityException


class OrdersHandler(Resource):
    """ Orders endpoint. """

    def get(self):
        """ Get all the orders."""
        retval = []

        for order in Order.select():
            retval.append(order.json(include_items=True))

        return retval, OK

    @auth.login_required
    def post(self):
        """ Insert a new order."""
        user = g.user
        res = request.get_json(force=True)
        # Check that the order has an 'items' and 'delivery_address' attributes
        # otherwise it's useless to continue.
        for key in ('items', 'delivery_address'):
            if not res['order'].get(key):
                return None, BAD_REQUEST

        res_items = res['order']['items']

        # Check that the items exist
        item_uuids = [res_item['item_uuid'] for res_item in res_items]
        items = Item.select().where(Item.uuid << item_uuids)
        if items.count() != len(res_items):
            abort(BAD_REQUEST)

        # Check that the address exist
        try:
            address = Address.get(Address.uuid == res['order']['delivery_address'])
        except Address.DoesNotExist:
            abort(BAD_REQUEST)

        with database.atomic():
            try:
                order = Order.create(
                    delivery_address=address,
                    user=user,
                )

                # Generate the dict of {<Item>: <int:quantity>} to call Order.add_items
                items_to_add = {}
                for res_item in res_items:
                    item = next(i for i in items if str(i.uuid) == res_item['item_uuid'])
                    items_to_add[item] = res_item['quantity']
                order.update_items(items_to_add)
            except InsufficientAvailabilityException:
                abort(BAD_REQUEST)

        return order.json(include_items=True), CREATED


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_uuid):
        """ Get a specific order, including all the related Item(s)."""
        try:
            order = Order.get(Order.uuid == order_uuid)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        return order.json(include_items=True), OK

    @auth.login_required
    def patch(self, order_uuid):
        """ Modify a specific order. """
        res = request.get_json(force=True)
        for key in ('items', 'delivery_address', 'uuid'):
            if not res['order'].get(key):
                return None, BAD_REQUEST

        with database.atomic():
            try:
                order = Order.get(uuid=str(order_uuid))
            except Order.DoesNotExist:
                abort(NOT_FOUND)

            try:
                address = Address.get(Address.uuid == res['order']['delivery_address'])
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
            items_uuids = [e['item_uuid'] for e in res['order']['items']]
            items = list(Item.select().where(Item.uuid << items_uuids))
            if len(items) != len(items_uuids):
                abort(BAD_REQUEST)
            items_to_add = {
                item: req_item['quantity']
                for item in items for req_item in res['order']['items']
                if str(item.uuid) == req_item['item_uuid']
            }
            try:
                order.update_items(items_to_add)
            except InsufficientAvailabilityException:
                abort(BAD_REQUEST)

        return order.json(include_items=True), OK

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
