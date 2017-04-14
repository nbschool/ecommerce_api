"""
Test suite.
"""

from models import Order, OrderItem, Item
from tests.test_utils import open_with_auth, add_user
from tests.test_case import TestCase
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from peewee import SqliteDatabase
import json
from uuid import uuid4

# main endpoint for API
API_ENDPOINT = '/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'


class TestOrders(TestCase):

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_orders(self):
        item = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )

        user_A = add_user(None, TEST_USER_PSW)
        order = Order.create(delivery_address='Via Rossi 12', user=user_A)
        order.add_item(item, 2)

        resp = self.app.get('/orders/')

        expected_data = [{
            'order_id': str(order.order_id),
            'date': str(order.created_at),
            'total_price': 40.40,
            'user_id': str(user_A.user_id),
            'delivery_address': 'Via Rossi 12',
            'items': [{
                'quantity': 2,
                'subtotal': 40.40,
                'price': 20.20,
                'name': 'mario',
                'description': 'svariati mariii'
            }]
        }]

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_data

    def test_get_order__non_existing_empty_orders(self):
        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__non_existing(self):
        user_A = add_user(None, TEST_USER_PSW)
        Order.create(delivery_address='Via Rossi 12', user=user_A)

        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order(self):
        user = add_user(None, TEST_USER_PSW)

        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        item2 = Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=3
        )

        order1 = Order.create(delivery_address='Via Rossi 12', user=user)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address='Via Verdi 12', user=user)
        order2.add_item(item1).add_item(item2, 2)

        expected_data = {
            'order_id': str(order1.order_id),
            'date': str(order1.created_at),
            'user_id': str(user.user_id),
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
            description='svariati mariii',
            availability=4
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('123@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': {
                    'mario': {'price': 20.20, 'quantity': 4},
                    'GINO': {'price': 30.20, 'quantity': 10}
                },
                'delivery_address': 'Via Rossi 12',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }

        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == CREATED
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 2

        total_price = 0
        for _, values in order['order']['items'].items():
            total_price += (values['price'] * values['quantity'])

        data = json.loads(resp.data)

        assert data['total_price'] == total_price
        assert data['delivery_address'] == order['order']['delivery_address']
        assert Order.get().json()['order_id'] == data['order_id']

    def test_create_order__failure_availability(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order = {
            'order': {
                'items': {
                    'item1': {'price': 10.10, 'quantity': 3}
                }
            }
        }
        user_A = add_user('123@email.com', TEST_USER_PSW)
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_missing_field(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': {
                    'item1': {'price': 50.0, 'quantity': 4},
                    'item2': {'price': 20.0, 'quantity': 10}
                },
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_empty_field(self):
        Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': {
                    'mario': {'price': 50.0, 'quantity': 4},
                    'GINO': {'price': 20.0, 'quantity': 10}
                },
                'delivery_address': '',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order_no_items__fail(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': [],
                'delivery_address': 'Via Antani 2',
                'user': str(user.user_id)
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_update_order__success(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=5
        )
        item2 = Item.create(
            item_id='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order1 = Order.create(delivery_address='Via Rossi 12', user=user_A)
        order1.add_item(item1, 2).add_item(item2)

        order2 = Order.create(delivery_address='Via Bianchi 10', user=user_A)
        order2.add_item(item2)

        order_id = str(order1.order_id)

        order = {
            "order": {
                "order_id": order_id,
                'items': {
                    'mario': {'price': 20.0, 'quantity': 5},
                    'GINO': {'price': 30.20, 'quantity': 1}
                },
                'delivery_address': 'Via Verdi 20',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == OK
        resp_order = Order.get(order_id=order1.order_id).json()
        assert resp_order['order_id'] == order['order']['order_id']
        assert resp_order['delivery_address'] == order['order']['delivery_address']

    def test_update_order_empty_items_list__fail(self):
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii'
        )
        user = add_user('12345@email.com', TEST_USER_PSW)

        order = Order.create(
            delivery_address='Via Rossi 12',
            user=user
        ).add_item(item1, 2)

        order_id = str(order.order_id)

        order_data = {
            "order": {
                "order_id": order_id,
                'items': [],
                'delivery_address': 'Via Verdi 20',
                'user': str(user.user_id)

            }
        }
        path = 'orders/{}'.format(order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order_data))

        assert resp.status_code == BAD_REQUEST
        assert len(order.order_items) == 1

    def test_update_order__failure_non_existing(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        Order.create(delivery_address='Via Rossi 12', user=user_A)

        order_id = str(uuid4())

        order = {
            "order": {
                "order_id": order_id,
                'items': {
                    'item1': {'price': 100.0, 'quantity': 5},
                    'item2': {'price': 2222.0, 'quantity': 1}
                },
                'delivery_address': 'Via Verdi 20'
            }
        }

        path = 'orders/{}'.format(order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == NOT_FOUND

    def test_update_order__failure_availability(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        item = Item.create(
            item_id=uuid4(),
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order = Order.create(
            delivery_address='Via Rossi 12',
            user=user_A
        )
        OrderItem.create(
            order=order,
            item=item,
            quantity=2,
            subtotal=50.00
        )

        update_order = {
            "order": {
                "order_id": str(order.order_id),
                'items': {
                    'mario': {'price': 30.30, 'quantity': 3},
                },
                'delivery_address': 'Via Verdi 20'
            }
        }

        path = 'orders/{}'.format(order.order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PUT',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(update_order))

        assert resp.status_code == BAD_REQUEST

    def test_update_order__failure_non_existing_empty_orders(self):
        add_user('user@email.com', TEST_USER_PSW)
        order_id = str(uuid4())
        order = {
            "order": {
                "order_id": order_id,
                'items': {
                    'item1': {'price': 100.0, 'quantity': 5},
                    'item2': {'price': 2222.0, 'quantity': 1}
                },
                'delivery_address': 'Via Verdi 20',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = '/orders/{}'.format(order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PUT',
                              'user@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == NOT_FOUND

    def test_delete_order__success(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        item1 = Item.create(
            item_id='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address='Via Rossi 12', user=user_A)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address='Via Verdi 12', user=user_A)

        resp = self.app.delete('/orders/{}'.format(order1.order_id))

        path = 'orders/{}'.format(order1.order_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              '12345@email.com', TEST_USER_PSW, None,
                              None)

        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(order_id=order2.order_id)

    def test_delete_order__failure_non_existing_empty_orders(self):

        user_A = add_user('12345@email.com', TEST_USER_PSW)

        path = 'orders/{}'.format(str(uuid4()))
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_A.email, TEST_USER_PSW, None,
                              None)
        assert resp.status_code == NOT_FOUND

    def test_delete_order__failure__failure_non_existing(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        Order.create(delivery_address='Via Rossi 12', user=user_A)

        resp = self.app.delete('/orders/{}'.format(uuid4()))

        path = 'orders/{}'.format(str(uuid4()))
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_A.email, TEST_USER_PSW, None,
                              None)
        assert resp.status_code == NOT_FOUND
        assert Order.select().count() == 1

    def test_order_items_management(self):
        """
        Test add_item and remove_item function from Order and OrderItem
        models.
        """
        user = add_user(None, TEST_USER_PSW)

        def count_items(order):
            tot = 0
            for oi in order.order_items:
                tot += oi.quantity
            return tot

        item1 = Item.create(
            item_id=uuid4(),
            name='Item',
            description='Item description',
            price=10,
            availability=2
        )
        item2 = Item.create(
            item_id=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=15,
            availability=2
        )
        item3 = Item.create(
            item_id=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=15,
            availability=2
        )
        order = Order.create(delivery_address='My address', user=user)
        order.add_item(item1, 2).add_item(item2, 2)

        assert len(order.order_items) == 2
        assert OrderItem.select().count() == 2
        assert count_items(order) == 4

        # test removing one of two item1
        order.remove_item(item1)
        assert len(order.order_items) == 2
        assert count_items(order) == 3

        # remove more item1 than existing in order
        order.remove_item(item1, 5)
        assert len(order.order_items) == 1
        assert OrderItem.select().count() == 1
        assert count_items(order) == 2

        # Check that the total price is correctly updated
        assert order.total_price == item2.price * 2

        # remove non existing item3 from order
        order.remove_item(item3)
        assert count_items(order) == 2
        assert len(order.order_items) == 1

        order.empty_order()
        assert len(order.order_items) == 0
        assert OrderItem.select().count() == 0
