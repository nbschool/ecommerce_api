"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from flask_restful import Resource
from models import Address, Order, Item
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST, UNAUTHORIZED
from flask import abort, request, g
from auth import auth


def serialize_order(order_obj):
    """
    From a Order object create a json-serializable dict with all the order
    information, including all the OrderItem(s) - and related Item(s) -
    properties.
    """

    order = order_obj.json()
    order['items'] = []

    for orderitem in order_obj.order_items:
        # serialize the Item(s) for the order, adding the info stored into
        # the OrderItem table related to the order/item, into the 'items'
        # property of the return value
        order['items'].append({
            'quantity': orderitem.quantity,
            'price': float(orderitem.item.price),
            'subtotal': float(orderitem.subtotal),
            'name': orderitem.item.name,
            'description': orderitem.item.description
        })
    return order


class OrdersHandler(Resource):
    """ Orders endpoint. """

    def get(self):
        """ Get all the orders."""
        retval = []

        for order in Order.select():
            retval.append(serialize_order(order))

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

        # Check that the items exist by getting all the item names from the
        # request and executing a get() request with Peewee
        item_ids = list(map(lambda x: x['item_id'], res_items))
        items = Item.select().where(Item.item_id << item_ids)

        if items.count() != len(res_items):
            abort(BAD_REQUEST)

        # check whether availabilities allow orders
        if any(item.availability < res_item['quantity'] for item in items 
                for res_item in res_items if item.item_id == res_item['item_id']):
            return None, BAD_REQUEST
        
        # Check that the order has an 'items' and 'delivery_address' attributes
        # otherwise it's useless to continue.
        for i in ('items', 'delivery_address'):
            if not res['order'].get(i):
                return None, BAD_REQUEST

        # Check that the address exist and check that the items exist by getting all the item names
        # from the request and executing a get() request with Peewee
        try:
            items_ids = [e['item_id'] for e in res['order']['items']]
            address = Address.get(Address.address_id == res['order']['delivery_address'])
            items = list(Item.select().where(Item.item_id << items_ids))
            if len(items) != len(items_ids):
                return None, BAD_REQUEST
        except Address.DoesNotExist:
            abort(BAD_REQUEST)

        order = Order.create(
            delivery_address=address,
            user=user,
        )

        for item in items:
            for res_item in res_items:
                # if names match add item and quantity, once per res_item
                if item.item_id == res_item['item_id']:
                    order.add_item(item, res_item['quantity'])
                    break

        return serialize_order(order), CREATED


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_id):
        """ Get a specific order, including all the related Item(s)."""
        try:
            order = Order.get(Order.order_id == order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        return serialize_order(order), OK

    @auth.login_required
    def patch(self, order_id):
        """ Modify a specific order. """
        res = request.get_json()
        res_items = res['order']['items']

        for key in ('items', 'delivery_address', 'order_id'):
            if not res['order'].get(key):
                return None, BAD_REQUEST

        try:
            order = Order.get(order_id=str(order_id))
            address = Address.get(Address.address_id == res['order']['delivery_address'])
            items_ids = [res_item['item_id'] for res_item in res_items]
            items = list(Item.select().where(Item.item_id << items_ids))
            if len(items) != len(items_ids):
                return None, BAD_REQUEST
        except (Address.DoesNotExist, Order.DoesNotExist):
            return None, NOT_FOUND

        # get the user from the flask.g global object registered inside the
        # auth.py::verify() function, called by @auth.login_required decorator
        # and match it against the found user.
        # This is to prevent users from modify other users' order.
        if g.user != order.user and g.user.admin is False:
            return ({'message': "You can't delete another user's order"},
                    UNAUTHORIZED)

        # check whether availabilities allow order update
        if any(item.availability < res_item['quantity'] for item in items 
                for res_item in res_items if item.item_id == res_item['item_id']):
            return None, BAD_REQUEST

        # Clear the order of all items before adding the new items
        # that came with the PATCH request
        order.empty_order()

        for item in items:
            for res_item in res_items:
                # if names match add item and quantity, once per res_item
                if item.item_id == res_item['item_id']:
                    order.add_item(item, res_item['quantity'])
                    break

        order.delivery_address = address
        order.save()

        return serialize_order(order), OK

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
