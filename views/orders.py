"""
Orders-view: this module contains functions for the interaction with the orders.
"""

from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
import datetime
import uuid
from models import Order, OrderItem, Item
from flask import abort, request


class OrdersHandler(Resource):
    """ Orders endpoint. """

    def get(self):
        """ Get all the orders."""
        orders = {}

        res = (
            Order
            .select(Order, OrderItem, Item)
            .join(OrderItem)
            .join(Item)
        )

        for row in res:
            if row.order_id not in orders:
                orders[row.order_id] = {
                    'order_id': str(row.order_id),
                    'date': row.date,
                    'total_price': float(row.total_price),
                    'delivery_address': row.delivery_address,
                    'items': []
                }
            orders[row.order_id]['items'].append({
                'quantity': row.orderitem.quantity,
                'subtotal': float(row.orderitem.subtotal),
                'item_name': row.orderitem.item.name,
                'item_description': row.orderitem.item.description
            })
        return list(orders.values()), OK

    def post(self):
        """ Insert a new order."""
        res = request.get_json()
        try:
            item_names = [e['name'] for e in res['order']['items']]
            Item.get(Item.name << item_names)

        except Item.DoesNotExist:
            abort(BAD_REQUEST)

        for i in ('items', 'delivery_address'):
            if i not in res['order']:
                return None, BAD_REQUEST

        for i in ('items', 'delivery_address'):
            if not res['order'][i]:
                return None, BAD_REQUEST

        order1 = Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=0,
            delivery_address=res['order']['delivery_address'],
        )

        for item in res['order']['items']:
            subtotal = item['price'] * item['quantity']
            OrderItem.create(
                order=order1,
                item=Item.get(name=(item['name'])),
                quantity=item['quantity'],
                subtotal=subtotal
            )
            order1.total_price += subtotal

        return order1.json(), CREATED


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_id):
        """ Get a specific order. """
        try:
            order = Order.get(Order.order_id == order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        retval = order.json()
        retval['items'] = []

        for orderitem in order.order_items:
            retval['items'].append({
                'quantity': orderitem.quantity,
                'subtotal': float(orderitem.subtotal),
                'name': orderitem.item.name,
                'description': orderitem.item.description
            })

        return retval, OK

    def put(self, order_id):
        """ Modify a specific order. """
        res = request.get_json()

        try:
            order_to_modify = Order.get(order_id=str(order_id))
        except Order.DoesNotExist:
            return None, NOT_FOUND

        for i in ('items', 'delivery_address', 'order_id'):
            if i not in res['order']:
                return None, BAD_REQUEST

        for i in ('items', 'delivery_address', 'order_id'):
            if not res['order'][i]:
                return None, BAD_REQUEST

        try:
            OrderItem.delete().where(OrderItem.order == order_to_modify).execute()
        except OrderItem.DoesNotExist:
            return None, NOT_FOUND

        order_to_modify.total_price = 0
        for item in res['order']['items']:
            OrderItem.create(
                order=order_to_modify,
                item=Item.get(name=(item['name'])),
                quantity=item['quantity'],
                subtotal=item['price'] * item['quantity']
            )
            order_to_modify.total_price += item['price']
        order_to_modify.date = datetime.datetime.now().isoformat()
        order_to_modify.delivery_address = res['order']['delivery_address']
        order_to_modify.save()

        return order_to_modify.json(), OK

    def delete(self, order_id):
        """ Delete a specific order. """
        try:
            obj = Order.get(order_id=str(order_id))
        except Order.DoesNotExist:
            return None, NOT_FOUND

        obj.delete_instance(recursive=True)
        return None, NO_CONTENT
