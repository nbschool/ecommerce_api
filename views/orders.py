"""
Orders-view: this module contains functions for the interaction with the orders.
"""

import random
from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth
from base64 import b64encode
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
import datetime
import uuid
from models import Order, OrderItem, Item, User
from flask import abort, request, g
from auth import auth


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

    @auth.login_required
    def post(self):
        """ Insert a new order."""
        user = g.user
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
            user=user
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

        serialized = order1.json()
        # serialized['user'] = order1.user.json()
        return serialized, CREATED


class OrderHandler(Resource):
    """ Single order endpoints."""

    def get(self, order_id):
        """ Get a specific order. """
        res = (
            Order
            .select(Order, OrderItem, Item)
            .join(OrderItem)
            .join(Item)
            .where(Order.order_id == order_id)
        )

        if not res:
            return None, NOT_FOUND

        order = {
            'order_id': str(res[0].order_id),
            'date': res[0].date,
            'total_price': float(res[0].total_price),
            'delivery_address': res[0].delivery_address,
            'items': []
        }
        for row in res:
            order['items'].append({'quantity': row.orderitem.quantity,
                                   'subtotal': float(row.orderitem.subtotal),
                                   'item_name': row.orderitem.item.name,
                                   'item_description': row.orderitem.item.description
                                   })
        return list(order.values()), OK

    @auth.login_required
    def put(self, order_id):
        """ Modify a specific order. """
        user = g.user
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

    @auth.login_required
    def delete(self, order_id):
        """ Delete a specific order. """
        try:
            obj = Order.get(order_id=str(order_id))
        except Order.DoesNotExist:
            return None, NOT_FOUND

        obj.delete_instance(recursive=True)
        return None, NO_CONTENT