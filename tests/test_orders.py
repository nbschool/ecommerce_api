"""
Test suite.
"""

from app import app
from models import Order, OrderItem, Item, User
from tests.test_utils import open_with_auth, add_user
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from peewee import SqliteDatabase
import datetime
import json
import random
import uuid

# main endpoint for API
API_ENDPOINT = '/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'


class TestOrders:
    @classmethod 
    def setup_class(cls):
        test_db = SqliteDatabase(':memory:')
        Order._meta.database = test_db
        Item._meta.database = test_db
        OrderItem._meta.database = test_db
        User._meta.database = test_db
        test_db.connect()
        Order.create_table()
        Item.create_table()
        OrderItem.create_table()
        User.create_table()
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
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        user_A = add_user(None, TEST_USER_PSW)
        order_id =  uuid.uuid4()
        dt = datetime.datetime.now().isoformat()
        order1 = Order.create(
            order_id=order_id,
            date=dt,
            total_price=100.00,
            delivery_address='Via Rossi 12',
            user=user_A
        )
        OrderItem.create(
            order=order1,
            item=item1,
            quantity=2,
            subtotal=50.00
        )
        resp = self.app.get('/orders/')

        assert resp.status_code == OK
        assert json.loads(resp.data) == [
            {
                "order_id": str(order_id), "date": dt, "total_price": 100.00,
                "delivery_address": 'Via Rossi 12',
                "items": [{
                    "quantity": 2, "subtotal": 50.00, "item_name": "mario", "item_description":
                    "svariati mariii"
                }]
            }
        ]

    def test_get_order__non_existing_empty_orders(self):
        resp = self.app.get('/orders/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__non_existing(self):
        user_A = add_user(None, TEST_USER_PSW)	
        Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=100,
            delivery_address='Via Rossi 12',
            user=user_A
        )
        resp = self.app.get('/orders/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        user_A = add_user(None, TEST_USER_PSW)
        order_id = uuid.uuid4()
        dt = datetime.datetime.now().isoformat()
        order1 = Order.create(
            order_id=order_id,
            date=dt,
            total_price=100,
            delivery_address='Via Rossi 12',
            user=user_A
        )
        OrderItem.create(
            order=order1,
            item=item1,
            quantity=2,
            subtotal=50.00
        )
        item2 = Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII'
        )
        order2 = Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=200,
            delivery_address='Via Verdi 12',
            user=user_A
        )
        OrderItem.create(
            order=order2,
            item=item2,
            quantity=3,
            subtotal=100.00
        )

        resp = self.app.get('/orders/{}'.format(order_id))
        assert resp.status_code == OK
        assert json.loads(resp.data) == [
            str(order_id), dt, 100.0, 'Via Rossi 12', [{
                "quantity": 2,
                "subtotal": 50.0,
                "item_name": "mario",
                "item_description":
                "svariati mariii"}]
        ]

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
        user_A = add_user(None, TEST_USER_PSW)
        order = {
            'order': {
                'items': [
                    {'name': 'mario', 'price': 20.20, 'quantity': 4},
                    {'name': 'GINO', 'price': 30.20, 'quantity': 10}
                ],
                'delivery_address': 'Via Rossi 12',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                                   user_A.email, TEST_USER_PSW, 'application/json',
                            	   json.dumps(order))

        assert resp.status_code == CREATED
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 2

        total_price = 0
        for p in order['order']['items']:
            total_price += (p['price'] * p['quantity'])

        assert json.loads(resp.data)['total_price'] == total_price
        assert json.loads(resp.data)['delivery_address'] == order[
            'order']['delivery_address']
        assert json.loads(resp.data)['order_id']
        assert Order.get().json()['order_id'] == json.loads(
            resp.data)['order_id']

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
                'delivery_address': '',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
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

        user_A = add_user(None, TEST_USER_PSW)

        order1 = Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=100,
            delivery_address='Via Rossi 12',
            user=user_A
        )
        OrderItem.create(
            order=order1,
            item=item1,
            quantity=2,
            subtotal=40.00
        )
        OrderItem.create(
            order=order1,
            item=item2,
            quantity=1,
            subtotal=60
        )
        order2 = Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=60,
            delivery_address='Via Bianchi 10',
            user=user_A
        )
        OrderItem.create(
            order=order2,
            item=item2,
            quantity=1,
            subtotal=60
        )
        order_id = str(order1.order_id)
        order = {
            "order": {
                "order_id": order_id,
                'items': [
                    {'name': 'mario', 'price': 20.0, 'quantity': 5},
                    {'name': 'GINO', 'price': 30.20, 'quantity': 1}
                ],
                'delivery_address': 'Via Verdi 20',
				'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        resp = self.app.put('/orders/{}'.format(order1.order_id),
                            data=json.dumps(order),
                            content_type='application/json')
        assert resp.status_code == OK
        modified_order = Order.get(order_id=order1.order_id).json()
        assert modified_order['order_id'] == order['order']['order_id']
        assert modified_order['delivery_address'] == order[
            'order']['delivery_address']

    def test_update_order__failure_non_existing(self):
        Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=100,
            delivery_address='Via Rossi 12'
        )
        order_id = str(uuid.uuid4())
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
        order_id = str(uuid.uuid4())
        order = {
            "order": {
                "order_id": order_id,
                'items': [
                    {'name': 'item1', 'price': 100.0, 'quantity': 5},
                    {'name': 'item2', 'price': 2222.0, 'quantity': 1}
                ],
                'delivery_address': 'Via Verdi 20',
				'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        self.app.put('/orders/{}'.format(order_id),
                     data=json.dumps(order), content_type='application/json')

    def test_delete_order__success(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        order_id = uuid.uuid4()
        dt = datetime.datetime.now().isoformat()
        order1 = Order.create(
            order_id=order_id,
            date=dt,
            total_price=100,
            delivery_address='Via Rossi 12'
        )
        OrderItem.create(
            order=order1,
            item=item1,
            quantity=2,
            subtotal=50.00
        )
        order2 = Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=200,
            delivery_address='Via Verdi 12'
        )
        resp = self.app.delete('/orders/{}'.format(str(order_id)))
        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(order_id=order2.order_id)

    def test_delete_order__failure_non_existing_empty_orders(self):
        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_delete_order__failure__failure_non_existing(self):
        user_A = add_user(None, TEST_USER_PSW)  
        Order.create(
            order_id=uuid.uuid4(),
            date=datetime.datetime.now().isoformat(),
            total_price=100,
            delivery_address='Via Rossi 12',
            user=user_A
        )
        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
        assert len(Order.select()) == 1
