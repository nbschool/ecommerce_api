"""
Test suite.
"""

from app import app
from models import Order, OrderItem, Item
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from peewee import SqliteDatabase
import json
from uuid import uuid4


class TestOrders:
    @classmethod
    def setup_class(cls):
        test_db = SqliteDatabase(':memory:')
        Order._meta.database = test_db
        Item._meta.database = test_db
        OrderItem._meta.database = test_db
        test_db.connect()
        Order.create_table()
        Item.create_table()
        OrderItem.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Order.delete().execute()
        Item.delete().execute()
        OrderItem.delete().execute()

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_orders(self):
        item = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )

        order = Order.create(delivery_address='Via Rossi 12')
        order.add_item(item)
        order.add_item(item)

        resp = self.app.get('/orders/')

        expected_data = [{
            "order_id": str(order.order_id),
            "date": str(order.created_at),
            "total_price": 40.40,
            "delivery_address": 'Via Rossi 12',
            "items": [{
                "quantity": 2,
                "subtotal": 40.40,
                "price": 20.20,
                "name": "mario",
                "description": "svariati mariii"
            }]
        }]

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_data

    def test_get_order__non_existing_empty_orders(self):
        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__non_existing(self):
        Order.create(delivery_address='Via Rossi 12')

        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )

        item2 = Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )

        order1 = Order.create(delivery_address='Via Rossi 12')
        order1.add_item(item1)
        order1.add_item(item1)

        order2 = Order.create(delivery_address='Via Verdi 12')
        order2.add_item(item2)
        order2.add_item(item2)
        order2.add_item(item2)

        expected_data = {
            'order_id': str(order1.order_id),
            'date': str(order1.created_at),
            'total_price': 40.40,
            'delivery_address': 'Via Rossi 12',
            'items': [{
                'quantity': 2,
                'subtotal': 40.40,
                "price": 20.20,
                'name': 'mario',
                'description': 'svariati mariii'
            }]
        }

        resp = self.app.get('/orders/{}'.format(order1.order_id))
        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_data

    def test_create_order__success(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )

        order = {
            'order': {
                'items': [
                    {'name': 'mario', 'price': 20.20, 'quantity': 4},
                    {'name': 'GINO', 'price': 30.20, 'quantity': 10}
                ],
                'delivery_address': 'Via Rossi 12'
            }
        }
        resp = self.app.post('/orders/', data=json.dumps(order),
                             content_type='application/json')

        assert resp.status_code == CREATED
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 2
        # assert

        total_price = 0
        for p in order['order']['items']:
            total_price += (p['price'] * p['quantity'])

        data = json.loads(resp.data)

        assert data['total_price'] == total_price
        assert data['delivery_address'] == order['order']['delivery_address']
        assert Order.get().json()['order_id'] == data['order_id']

    def test_create_order__failure_missing_field(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )
        order = {
            'order': {
                'items': [
                    {'name': 'item1', 'price': 50.0, 'quantity': 4},
                    {'name': 'item2', 'price': 20.0, 'quantity': 10}
                ]
            }
        }
        resp = self.app.post('/orders/', data=json.dumps(order),
                             content_type='application/json')
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_empty_field(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )

        order = {
            'order': {
                'items': [
                    {'name': 'item1', 'price': 50.0, 'quantity': 4},
                    {'name': 'item2', 'price': 20.0, 'quantity': 10}
                ],
                'delivery_address': ''
            }
        }
        resp = self.app.post('/orders/', data=json.dumps(order),
                             content_type='application/json')
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_update_order__success(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        item2 = Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )
        order1 = Order.create(delivery_address='Via Rossi 12')
        order1.add_item(item1)
        order1.add_item(item1)
        order1.add_item(item2)

        order2 = Order.create(delivery_address='Via Bianchi 10')
        order2.add_item(item2)

        order_id = str(order1.order_id)

        order = {
            "order": {
                "order_id": order_id,
                'items': [
                    {'name': 'mario', 'price': 20.0, 'quantity': 5},
                    {'name': 'GINO', 'price': 30.20, 'quantity': 1}
                ],
                'delivery_address': 'Via Verdi 20'
            }
        }
        resp = self.app.put('/orders/{}'.format(order1.order_id),
                            data=json.dumps(order),
                            content_type='application/json')
        assert resp.status_code == OK
        resp_order = Order.get(order_id=order1.order_id).json()
        assert resp_order['order_id'] == order['order']['order_id']
        assert resp_order['delivery_address'] == order['order']['delivery_address']

    def test_update_order__failure_non_existing(self):
        Order.create(delivery_address='Via Rossi 12')

        order_id = str(uuid4())

        order = {
            "order": {
                "order_id": order_id,
                'items': [
                    {'name': 'item1', 'price': 100.0, 'quantity': 5},
                    {'name': 'item2', 'price': 2222.0, 'quantity': 1}
                ],
                'delivery_address': 'Via Verdi 20'
            }
        }

        resp = self.app.put('/orders/{}'.format(order_id),
                            data=json.dumps(order),
                            content_type='application/json')
        assert resp.status_code == NOT_FOUND

    def test_update_order__failure_non_existing_empty_orders(self):
        order_id = str(uuid4())
        order = {
            "order": {
                "order_id": order_id,
                'items': [
                    {'name': 'item1', 'price': 100.0, 'quantity': 5},
                    {'name': 'item2', 'price': 2222.0, 'quantity': 1}
                ],
                'delivery_address': 'Via Verdi 20'
            }
        }
        resp = self.app.put('/orders/{}'.format(order_id),
                            data=json.dumps(order),
                            content_type='application/json')

        assert resp.status_code == NOT_FOUND

    def test_delete_order__success(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )

        order1 = Order.create(delivery_address='Via Rossi 12')
        order1.add_item(item1)
        order1.add_item(item1)

        order2 = Order.create(delivery_address='Via Verdi 12')

        resp = self.app.delete('/orders/{}'.format(order1.order_id))
        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(order_id=order2.order_id)

    def test_delete_order__failure_non_existing_empty_orders(self):
        resp = self.app.delete('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_delete_order__failure__failure_non_existing(self):
        Order.create(delivery_address='Via Rossi 12')

        resp = self.app.delete('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Order.select()) == 1

    def test_order_items_management(self):
        """
        Test add_item and remove_item function from Order and OrderItem
        models.
        """

        def count_items(order):
            tot = 0
            for oi in order.order_items:
                tot += oi.quantity
            return tot

        item1 = Item.create(
            item_id=uuid4(),
            name='Item',
            description='Item description',
            price=10
        )
        item2 = Item.create(
            item_id=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=15
        )
        item3 = Item.create(
            item_id=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=15
        )
        order = Order.create(delivery_address='My address')
        order.add_item(item1, 2)
        order.add_item(item2, 2)

        assert len(order.order_items) == 2
        assert OrderItem.select().count() == 2
        assert count_items(order) == 4

        # test removing one of two item1
        order.remove_item(item1)
        assert len(order.order_items) == 2
        assert count_items(order) == 3

        # remove more item1 than existing in order
        order.remove_item(item1, 2)
        assert len(order.order_items) == 1
        assert OrderItem.select().count() == 1
        assert count_items(order) == 2

        # remove non existing item3 from order
        res = order.remove_item(item3)
        assert res is False
        assert count_items(order) == 2
        assert len(order.order_items) == 1
