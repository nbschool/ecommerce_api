"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from http.client import (BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK,
                         UNAUTHORIZED)

from flask import abort, g, request
from flask_restful import Resource

from models import database, Address, Order, Item
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

        with database.transaction() as txn:
            try:
                order = Order.create(
                    delivery_address=address,
                    user=g.user,
                )

                for item in items:
                    for req_item in req_items:
                        # if names match add item and quantity, once per
                        # req_item
                        if str(item.uuid) == req_item['id']:
                            order.add_item(item, req_item['quantity'])
                            break
                notify_new_order(address=order.delivery_address, user=order.user)

            except InsufficientAvailabilityException:
                txn.rollback()
                return None, BAD_REQUEST
            except KeyError:
                # FIXME: This catch is required to catch missing quantity attribute
                # on the post request. This should be done from the validate_input
                # function but this needs to be implemented yet, so this prevents
                # raising KeyError later on when adding items
                msg = {
                    'message': 'Item {} missing quantity attribute'.format(item.uuid)
                }
                return msg, BAD_REQUEST

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

        with database.transaction() as txn:
            try:
                order = Order.get(uuid=str(order_uuid))
            except Order.DoesNotExist:
                abort(NOT_FOUND)

            # get the user from the flask.g global object registered inside the
            # auth.py::verify() function, called by @auth.login_required decorator
            # and match it against the found user.
            # This is to prevent uses from modify other users' order.
            if g.user != order.user and g.user.admin is False:
                return ({'message': "You can't delete another user's order"},
                        UNAUTHORIZED)

            if req_address:
                try:
                    address = Address.get(Address.uuid == req_address['data']['id'])
                    order.delivery_address = address
                except Address.DoesNotExist:
                    abort(BAD_REQUEST)

            if req_items:
                req_items = req_items['data']  # avoid refactoring everything
                items_uuids = [e['id'] for e in req_items]
                items_query = Item.select().where(Item.uuid << items_uuids)
                items = {str(item.uuid): item for item in items_query}

                if len(items) != len(items_uuids):
                    return None, BAD_REQUEST

                for req_item in req_items:
                    item = items[req_item['id']]
                    try:
                        order.update_item(item, req_item['quantity'])
                    except InsufficientAvailabilityException:
                        txn.rollback()
                        return None, BAD_REQUEST
                    except KeyError:
                        # FIXME: Prevent future KeyError when adding items. See post method
                        # for further info.
                        msg = {
                            'message': 'Item {} missing quantity attribute'.format(item.uuid)
                        }
                        return msg, BAD_REQUEST

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
