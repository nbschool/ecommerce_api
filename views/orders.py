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
        res = request.get_json()
        # Check that the order has an 'items' and 'delivery_address' attributes
        # otherwise it's useless to continue.
        for key in ('items', 'delivery_address'):
            if not res['order'].get(key):
                return None, BAD_REQUEST

        res_items = res['order']['items']

        # Check that the items exist
        item_ids = [res_item['item_id'] for res_item in res_items]
        items = Item.select().where(Item.item_id << item_ids)
        if items.count() != len(res_items):
            abort(BAD_REQUEST)

        # Check that the address exist
        try:
            address = Address.get(Address.address_id == res['order']['delivery_address'])
        except Address.DoesNotExist:
            abort(BAD_REQUEST)

        with database.transaction() as txn:
            try:
                order = Order.create(
                    delivery_address=address,
                    user=user,
                )

                for item in items:
                    for res_item in res_items:
                        # if names match add item and quantity, once per res_item
                        if str(item.item_id) == res_item['item_id']:
                            order.add_item(item, res_item['quantity'])
                            break
            except InsufficientAvailabilityException:
                txn.rollback()
                return None, BAD_REQUEST

        return order.json(include_items=True), CREATED


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_id):
        """ Get a specific order, including all the related Item(s)."""
        try:
            order = Order.get(Order.order_id == order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        return order.json(include_items=True), OK

    @auth.login_required
    def patch(self, order_id):
        """ Modify a specific order. """
        res = request.get_json()

        res_items = res['order'].get('items')
        res_address = res['order'].get('delivery_address')

        if res_items is not None and len(res_items) == 0:
            return None, BAD_REQUEST

        with database.transaction() as txn:
            try:
                order = Order.get(order_id=str(order_id))
            except Order.DoesNotExist:
                abort(NOT_FOUND)

            if res_address:
                try:
                    address = Address.get(Address.address_id == res_address)
                    order.delivery_address = address
                except Address.DoesNotExist:
                    abort(BAD_REQUEST)

            if res_items:
                items_ids = [e['item_id'] for e in res_items]
                items_query = Item.select().where(Item.item_id << items_ids)
                items = {str(item.item_id): item for item in items_query}

                if len(items) != len(items_ids):
                    return None, BAD_REQUEST

                for res_item in res_items:
                    try:
                        order.update_item(items[res_item['item_id']], res_item['quantity'])
                    except InsufficientAvailabilityException:
                        txn.rollback()
                        return None, BAD_REQUEST
            # get the user from the flask.g global object registered inside the
            # auth.py::verify() function, called by @auth.login_required decorator
            # and match it against the found user.
            # This is to prevent uses from modify other users' order.
            if g.user != order.user and g.user.admin is False:
                return ({'message': "You can't delete another user's order"},
                        UNAUTHORIZED)

            order.save()

        return order.json(include_items=True), OK

    @auth.login_required
    def delete(self, order_id):
        """ Delete a specific order. """
        try:
            obj = Order.get(order_id=str(order_id))
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
