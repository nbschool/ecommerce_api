"""
Test suite.
"""

from models import Order, OrderItem, Item, WrongQuantity
from tests.test_utils import (open_with_auth, add_user, add_address,
                              add_admin_user, get_expected_results, wrong_dump)
from tests.test_case import TestCase
from http.client import (CREATED, NO_CONTENT, NOT_FOUND,
                         OK, BAD_REQUEST, UNAUTHORIZED)
import json
import pytest
from uuid import uuid4
from datetime import timezone
# main endpoint for API
API_ENDPOINT = '/{}'
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'

EXPECTED_RESULTS = get_expected_results('orders')


def add_date(result, date):
    """
    Add the date from a response to an expected result and return it.
    If the result is a list (i.e. get on all orders), set the date for each
    item in the list
    """
    # FIXME: date string does not match with response string
    # '2017-04-26T13:02:13.817604+00:00',   --> response
    # '2017-04-26T13:02:13.817604',         --> added date
    date = date.replace(tzinfo=timezone.utc)
    if type(result) == list:
        for r in result:
            r['data']['attributes']['date'] = date.isoformat()
    else:
        result['data']['attributes']['date'] = date.isoformat()
    return result


class TestOrders(TestCase):

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_orders__success(self):
        item = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )

        user_A = add_user(
            None, TEST_USER_PSW, id='f3f72634-7054-43ef-9119-9e8f54a9531e')
        addr_A = add_address(
            user=user_A, id='85c6cba6-3ddd-4847-9d07-1337ff4e8506')
        order = Order.create(
            delivery_address=addr_A, user=user_A,
            order_id='06451e0a-8fa2-40d2-8c51-1af50d369ca6')
        order.add_item(item, 2)

        resp = self.app.get('/orders/')

        expected_data = add_date(
            EXPECTED_RESULTS['get_orders__success'], order.created_at)

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_data

    def test_get_order__non_existing_empty_orders(self):
        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__non_existing(self):
        user_A = add_user(None, TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        Order.create(delivery_address=addr_A, user=user_A)

        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__success(self):
        user = add_user(None, TEST_USER_PSW,
                        id='f79d9cd9-d5a3-4285-b6c0-54e0a8497b2a')
        addr_A = add_address(
            user=user, id='fe17b62d-9e02-4889-862f-5b3323e689f5')
        addr_B = add_address(user=user, city='Firenze', post_code='50132',
                             address='Via Rossi 10', phone='055432433',
                             id='03e071e4-e89e-46a3-8dfd-3da1bd52c02f')

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=3
        )

        order1 = Order.create(delivery_address=addr_A, user=user,
                              order_id='b975ed38-f426-4965-8633-85a48442aaa5')
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address=addr_B, user=user)
        order2.add_item(item1).add_item(item2, 2)

        resp = self.app.get('/orders/{}'.format(order1.uuid))
        expected_result = add_date(
            EXPECTED_RESULTS['get_order__success'], order1.created_at)

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_result

    def test_create_order__success(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user = add_user('123@email.com', TEST_USER_PSW,
                        id='e736a9a6-448b-4b92-9e38-4cf745b066db')
        add_address(user=user, id='8473fbaa-94f0-46db-939f-faae898f001c')

        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.20, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.20, 'quantity': 10}
                ],
                'delivery_address': '8473fbaa-94f0-46db-939f-faae898f001c',
                'user': 'e736a9a6-448b-4b92-9e38-4cf745b066db'
            }
        }

        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == CREATED

        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 2

        expected_result = add_date(
            EXPECTED_RESULTS['create_order__success'], Order.get().created_at)

        assert json.loads(resp.data) == expected_result

    def test_create_order__not_json_failure(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user = add_user('123@email.com', TEST_USER_PSW)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.20, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.20, 'quantity': 10}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }

        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              wrong_dump(order))

        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0
        assert len(OrderItem.select()) == 0

    def test_create_order__failure_availability(self, mocker):
        mocker.patch('views.orders.database', new=self.TEST_DB)
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        user = add_user('12345@email.com', TEST_USER_PSW)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'order': {
                'items': [
                    {
                        'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                        'price': 30.30,
                        'quantity': 3,
                    }
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
            }
        }
        user = add_user('123@email.com', TEST_USER_PSW)
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_missing_field(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 50.0, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 20.0, 'quantity': 10}
                ],
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__non_existing_address(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 50.0, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 20.0, 'quantity': 10}
                ],
                'delivery_address': '577ad826-a79d-41e9-a5b2-7955bcf09043',
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
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 50.0, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 20.0, 'quantity': 10}
                ],
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
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'order': {
                'items': [],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': str(user.uuid)
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__non_existing_item(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        add_address(user=user_A, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'order': {
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 50.0, 'quantity': 4},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf034r3',
                     'price': 20.0, 'quantity': 10}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_update_order__new_item(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=5
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=10
        )

        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        addr_B = add_address(user=user_A)

        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.2, 'quantity': 10},
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == OK
        resp_order = Order.get(uuid=order1.uuid).json(include_items=True)
        assert resp_order['uuid'] == order['order']['uuid']
        assert resp_order['delivery_address']['uuid'] == order['order']['delivery_address']
        order_items = [o.json() for o in OrderItem.select()]
        assert str(order_items[0]['item_uuid']) == item1.uuid
        assert str(order_items[1]['item_uuid']) == item2.uuid

    def test_update_order__item_quantity_zero(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(user=user)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order1 = Order.create(delivery_address=addr, user=user)
        order1.add_item(item1, 2).add_item(item2)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 0},
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == OK
        resp_order = Order.get(uuid=order1.uuid).json(include_items=True)
        assert resp_order['uuid'] == order['order']['uuid']
        assert resp_order['delivery_address']['uuid'] == order['order']['delivery_address']
        assert len(resp_order['items']) == 1
        assert str(OrderItem.get().item.uuid) == item2.uuid

    def test_update_order__remove_item_without_delete(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=10
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=20
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(user=user)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order1 = Order.create(delivery_address=addr, user=user)
        order1.add_item(item1, 10).add_item(item2, 20)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 5},
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == OK
        resp_order = Order.get(uuid=order1.uuid).json(include_items=True)
        assert resp_order['uuid'] == order['order']['uuid']
        assert resp_order['delivery_address']['uuid'] == order['order']['delivery_address']
        order_items = [o.json() for o in OrderItem.select()]
        assert str(order_items[0]['item_uuid']) == item1.uuid
        assert str(order_items[1]['item_uuid']) == item2.uuid
        assert order_items[0]['quantity'] == '5'
        assert order_items[1]['quantity'] == '20'

    def test_update_order__add_item(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=10
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=20
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order1 = Order.create(delivery_address=addr_A, user=user)
        order1.add_item(item1, 5).add_item(item2, 20)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 10},
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == OK
        resp_order = Order.get(uuid=order1.uuid).json(include_items=True)
        assert resp_order['uuid'] == order['order']['uuid']
        assert resp_order['delivery_address']['uuid'] == order['order']['delivery_address']
        order_items = [o.json() for o in OrderItem.select()]
        assert str(order_items[0]['item_uuid']) == item1.uuid
        assert str(order_items[1]['item_uuid']) == item2.uuid
        assert order_items[0]['quantity'] == '10'
        assert order_items[1]['quantity'] == '20'

    def test_update_order__success(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=5
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        addr_B = add_address(user=user_A)

        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2).add_item(item2)

        order2 = Order.create(delivery_address=addr_B, user=user_A)
        order2.add_item(item2)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.20, 'quantity': 1}
                ],
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == OK
        resp_order, _ = Order.get(order_id=order1.order_id).serialize()
        assert resp_order['uuid'] == order['order']['uuid']
        assert resp_order['delivery_address']['address_id'] == order['order']['delivery_address']

    def test_update_order__non_existing_items(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(user=user)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order1 = Order.create(delivery_address=addr, user=user)
        order1.add_item(item1, 2).add_item(item2)
        order_item_before = [o.json() for o in OrderItem.select()]
        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf00000',
                     'price': 30.20, 'quantity': 1},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf2222',
                     'price': 50.20, 'quantity': 1},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf9999',
                     'price': 90.20, 'quantity': 2}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        order_item_after = [o.json() for o in OrderItem.select()]
        assert resp.status_code == BAD_REQUEST
        assert order_item_before == order_item_after

    def test_update_order__non_existing_address(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)

        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2).add_item(item2)
        order_item_before = [o.json() for o in OrderItem.select()]
        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf00000',
                     'price': 30.20, 'quantity': 1},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf2222',
                     'price': 50.20, 'quantity': 1},
                ],
                'delivery_address': '577ad826-a79d-41e9-a5b2-7955bcf5423',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        order_item_after = [o.json() for o in OrderItem.select()]
        assert resp.status_code == BAD_REQUEST
        assert order_item_before == order_item_after

    def test_update_order__success_admin_not_own_order(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=5
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        addr_B = add_address(user=user_A)

        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2).add_item(item2)

        order2 = Order.create(delivery_address=addr_B, user=user_A)
        order2.add_item(item2)

        order_uuid = str(order1.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.20, 'quantity': 1}
                ],
                'delivery_address': str(addr_B.address_id),
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'

            }
        }

        user_B = add_admin_user('admin_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user_B.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == OK
        updated_order, errors = Order.get(order_id=order1.order_id).serialize()

        order_data = updated_order['data']
        assert order_data['id'] == order['order']['order_id']
        rels = order_data['relationships']
        assert rels['delivery_address']['data']['id'] == order['order']['delivery_address']

    def test_update_order_empty_items_list__fail(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order = Order.create(
            delivery_address=addr,
            user=user
        ).add_item(item1, 2)

        order_uuid = str(order.uuid)

        order_data = {
            "order": {
                "uuid": order_uuid,
                'items': [],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': str(user.uuid)

            }
        }
        path = 'orders/{}'.format(order_uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order_data))

        assert resp.status_code == BAD_REQUEST
        assert len(order.order_items) == 1

    def test_update_order__failure_non_existing(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        Order.create(delivery_address=addr, user=user)

        order_uuid = str(uuid4())

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 100.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 2222.0, 'quantity': 1}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8'
            }
        }

        path = 'orders/{}'.format(order_uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == NOT_FOUND

    def test_update_order__failure_availability(self, mocker):
        mocker.patch('views.orders.database', new=self.TEST_DB)
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        item = Item.create(
            uuid=uuid4(),
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=1
        )
        order = Order.create(
            delivery_address=addr,
            user=user,
        )
        order_item = OrderItem.create(
            order=order,
            item=item,
            quantity=2,
            subtotal=50.00,
        )

        update_order = {
            "order": {
                "uuid": str(order.uuid),
                'items': [{
                    'item_uuid': str(item.uuid),
                    'price': 30.30, 'quantity': 4,
                }],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8'
            }
        }

        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(update_order))

        assert resp.status_code == BAD_REQUEST
        assert Order.select().count() == 1
        assert Order.get() == order
        assert Item.select().count() == 1
        assert Item.get() == item
        assert OrderItem.select().count() == 1
        assert OrderItem.get() == order_item

    def test_update_order__failure_non_existing_empty_orders(self):
        user = add_user('user@email.com', TEST_USER_PSW)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order_uuid = str(uuid4())
        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 100.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 2222.0, 'quantity': 1}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = '/orders/{}'.format(order_uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              'user@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == NOT_FOUND

    def test_update_order__failure_not_own_order(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=5
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order = Order.create(
            delivery_address=addr,
            user=user,
        ).add_item(item1, 2).add_item(item2)

        order_uuid = str(order.uuid)

        order = {
            "order": {
                "uuid": order_uuid,
                'items': [
                    {'item_uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'price': 20.0, 'quantity': 5},
                    {'item_uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'price': 30.20, 'quantity': 1}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'

            }
        }
        user_B = add_user('wrong_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user_B.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == UNAUTHORIZED

    def test_delete_order__success(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        addr_B = add_address(user=user_A)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address=addr_B, user=user_A)

        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              '12345@email.com', TEST_USER_PSW, None,
                              None)

        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(uuid=order2.uuid)

    def test_delete_order__success_admin_not_own_order(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        addr_B = add_address(user=user_A)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address=addr_B, user=user_A)

        user_B = add_admin_user('admin_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_B.email, TEST_USER_PSW, None,
                              None)

        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(uuid=order2.uuid)

    def test_delete_order__fail_not_own_order(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user_A)
        order1.add_item(item1, 2)

        user_B = add_user('admin_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_B.email, TEST_USER_PSW, None,
                              None)

        assert resp.status_code == UNAUTHORIZED

    def test_delete_order__failure_non_existing_empty_orders(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)

        path = 'orders/{}'.format(str(uuid4()))
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_A.email, TEST_USER_PSW, None,
                              None)
        assert resp.status_code == NOT_FOUND

    def test_delete_order__failure__failure_non_existing(self):
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user_A)
        Order.create(delivery_address=addr_A, user=user_A)

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
        addr = add_address(user=user)

        def count_items(order):
            tot = 0
            for oi in order.order_items:
                tot += oi.quantity
            return tot

        item1 = Item.create(
            uuid=uuid4(),
            name='Item',
            description='Item description',
            price=10,
            availability=2
        )
        item2 = Item.create(
            uuid=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=15,
            availability=2
        )
        item3 = Item.create(
            uuid=uuid4(),
            name='Item 3',
            description='Item 3 description',
            price=15,
            availability=2
        )
        order = Order.create(delivery_address=addr, user=user)
        order.add_item(item1, 2).add_item(item2, 2)

        assert len(order.order_items) == 2
        assert OrderItem.select().count() == 2
        assert count_items(order) == 4

        # test removing one of two item1
        order.remove_item(item1)
        assert len(order.order_items) == 2
        assert count_items(order) == 3

        # remove more item1 than existing in order
        with pytest.raises(WrongQuantity):
            order.remove_item(item1, 5)
            assert len(order.order_items) == 2
            assert OrderItem.select().count() == 2
            assert count_items(order) == 4

        # Check that the total price is correctly updated
        assert order.total_price == item1.price + item2.price + item3.price

        # remove non existing item3 from order
        order.remove_item(item3)
        assert count_items(order) == 3
        assert len(order.order_items) == 2

        order.empty_order()
        assert len(order.order_items) == 0
        assert OrderItem.select().count() == 0
