"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address, Order, Item
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
        for i in ('items', 'delivery_address'):
            if not res['order'].get(i):
                return None, BAD_REQUEST

        # Check that the address exist and check that the items exist by getting all the item names
        # from the request and executing a get() request with Peewee
        try:
            item_names = [e['name'] for e in res['order']['items']]
            # FIXME: This look up just one item, not all of them, so it does
            # not work for testing that ALL the requested items exist
            # TODO: Use a query to get all the items and use the result to
            # add the items to the order instead of querying again below
            address = Address.get(Address.address_id == res['order']['delivery_address'])
            Item.get(Item.name << item_names)
        except (Address.DoesNotExist, Item.DoesNotExist):
            abort(BAD_REQUEST)

        order = Order.create(
            delivery_address=address,
            user=user,
        )

        for i in res['order']['items']:
            item = Item.get(Item.name == i['name'])
            order.add_item(item, i['quantity'])

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

        for i in ('items', 'delivery_address', 'order_id'):
            if not res['order'].get(i):
                return None, BAD_REQUEST

        try:
            order = Order.get(order_id=str(order_id))
            address = Address.get(Address.address_id == res['order']['delivery_address'])
        except (Address.DoesNotExist, Order.DoesNotExist):
            return None, NOT_FOUND
        # Clear the order of all items before adding the new items
        # that came with the PATCH request
        order.empty_order()

        for item in res['order']['items']:
            order.add_item(
                Item.get(Item.name == item['name']), item['quantity'])

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

        obj.delete_instance(recursive=True)
        return None, NO_CONTENT
