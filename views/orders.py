"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from http.client import (BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK,
                         UNAUTHORIZED)

from flask import abort, g, request
from flask_restful import Resource

from auth import auth
from models import database, Address, Item, Order
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

        isValid, errors = Order.validate_input(res)
        if not isValid:
            return errors, BAD_REQUEST

        # Extract data to create the new order
        res_items = res['data']['relationships']['items']['data']
        res_address = res['data']['relationships']['delivery_address']['data']

        # Check that the items exist
        item_uuids = [res_item['item_uuid'] for res_item in res_items]
        items = Item.select().where(Item.uuid << item_uuids)
        if items.count() != len(res_items):
            abort(BAD_REQUEST)

        # Check that the address exist
        try:
            address = Address.get(Address.address_id == res_address['id'])
        except Address.DoesNotExist:
            abort(BAD_REQUEST)

        with database.transaction() as txn:
            try:
                order = Order.create(
                    delivery_address=address,
                    user=g.user,
                )

                for item in items:
                    for res_item in res_items:
                        # if names match add item and quantity, once per
                        # res_item
                        if str(item.uuid) == res_item['id']:
                            order.add_item(item, res_item['quantity'])
                            break
            except InsufficientAvailabilityException:
                txn.rollback()
                return None, BAD_REQUEST

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

        isValid, errors = Order.validate_input(res)
        if not isValid:
            return errors, BAD_REQUEST

        res_items = res['data']['relationships']['items']['data']
        res_address = res['data']['relationships']['delivery_address']['data']

        with database.transaction() as txn:
            try:
                order = Order.get(uuid=str(order_uuid))
            except Order.DoesNotExist:
                abort(NOT_FOUND)

            if res_address:
                try:
                    address = Address.get(Address.uuid == res_address)
                    order.delivery_address = address
                except Address.DoesNotExist:
                    abort(BAD_REQUEST)

            if res_items:
                items_uuids = [e['id'] for e in res_items]
                items_query = Item.select().where(Item.uuid << items_uuids)
                items = {str(item.uuid): item for item in items_query}

                if len(items) != len(items_uuids):
                    return None, BAD_REQUEST

                for res_item in res_items:
                    try:
                        order.update_item(
                            items[res_item['id']], res_item['quantity'])
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
