"""
Test suite.
"""

from tests.test_case import TestCase

import json
from http.client import (BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK,
                         UNAUTHORIZED)


from uuid import uuid4
from models import Item, Order, OrderItem
from tests.test_utils import (add_address, add_admin_user, add_user,
                              format_jsonapi_request, RESULTS,
                              open_with_auth, wrong_dump)

# main endpoint for API
API_ENDPOINT = '/{}'

# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'

EXPECTED_RESULTS = RESULTS['orders']


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
            availability=12
        )
        user = add_user(
            None, TEST_USER_PSW, id='f3f72634-7054-43ef-9119-9e8f54a9531e')
        addr = add_address(
            user=user, id='85c6cba6-3ddd-4847-9d07-1337ff4e8506')
        Order.create(
            delivery_address=addr, user=user,
            uuid='06451e0a-8fa2-40d2-8c51-1af50d369ca6'
        ).add_item(item, 2)

        Order.create(
            delivery_address=addr, user=user,
            uuid='429994bf-784e-47cc-a823-e0c394b823e8'
        ).add_item(item, 5)

        resp = self.app.get('/orders/')

        expected_result = EXPECTED_RESULTS['get_orders__success']

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_result

    def test_get_order__non_existing_empty_orders(self):
        resp = self.app.get('/orders/{}'.format(uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__non_existing(self):
        user = add_user(None, TEST_USER_PSW)
        addr = add_address(user=user)
        Order.create(delivery_address=addr, user=user)

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
            availability=12
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=30
        )

        order1 = Order.create(
            delivery_address=addr_A, user=user,
            uuid='b975ed38-f426-4965-8633-85a48442aaa5',
        ).add_item(item1, 2)

        Order.create(
            delivery_address=addr_B, user=user
        ).add_item(item1).add_item(item2, 2)

        resp = self.app.get('/orders/{}'.format(order1.uuid))

        expected_result = EXPECTED_RESULTS['get_order__success']
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
            'relationships': {
                'items': [{
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    'type': 'item', 'quantity': 4
                }, {
                    'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                    'type': 'item', 'quantity': 10
                }],
                'delivery_address': {
                    'type': 'address',
                    'id': '8473fbaa-94f0-46db-939f-faae898f001c'
                },
                'user': {
                    'type': 'user',
                    'id': 'e736a9a6-448b-4b92-9e38-4cf745b066db'
                }
            }
        }
        data = format_jsonapi_request('order', order)

        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))

        assert resp.status_code == CREATED

        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 2
        order = Order.get()
        expected_result = EXPECTED_RESULTS['create_order__success']
        # inject the order id
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
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 4},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 10}
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
        user = add_user('123@email.com', TEST_USER_PSW,
                        id='e736a9a6-448b-4b92-9e38-4cf745b066db')
        add_address(user=user, id='8473fbaa-94f0-46db-939f-faae898f001c')
        order = {
            'relationships': {
                'items': [{
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    'type': 'item', 'quantity': 4
                }],
                'delivery_address': {
                    'type': 'address',
                    'id': '8473fbaa-94f0-46db-939f-faae898f001c'
                },
                'user': {
                    'type': 'user',
                    'id': 'e736a9a6-448b-4b92-9e38-4cf745b066db'
                }
            }
        }

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
        user = add_user('12345@email.com', TEST_USER_PSW)

        order = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 4},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 10}
                ],
                'user': {
                    'type': 'user',
                    'id': 'e736a9a6-448b-4b92-9e38-4cf745b066db'
                }
            }
        }
        data = format_jsonapi_request('order', order)

        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))
        assert resp.status_code == BAD_REQUEST
        expected_result = EXPECTED_RESULTS['create_order__failure_missing_field']
        assert json.loads(resp.data) == expected_result
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
        user = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'order': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 4},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 10}
                ],
                'delivery_address': '577ad826-a79d-41e9-a5b2-7955bcf09043',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
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
        user = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 4},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 10}
                ],
                'delivery_address': {
                    'type': 'address',
                    'id': '8473fbaa-94f0-46db-939f-faae898f001c'
                },
                'user': {
                    'type': 'user',
                    'id': ''
                }
            }
        }
        data = format_jsonapi_request('order', order)
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order_missing_item_qty__fail(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=25
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=25
        )
        user_A = add_user('12345@email.com', TEST_USER_PSW)
        order = {
            'relationships': {
                'items': [{
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    'type': 'item',
                }, {
                    'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                    'type': 'item', 'quantity': 10,
                }],
                'delivery_address': {
                    'type': 'address',
                    'id': '8473fbaa-94f0-46db-939f-faae898f001c'
                },
                'user': {
                    'type': 'user',
                    'id': ''
                }
            }
        }
        data = format_jsonapi_request('order', order)
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user_A.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order_no_items__fail(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(
            user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'relationships': {
                'items': [],
                'delivery_address': {
                    'type': 'address',
                    'id': str(addr.uuid)
                },
                'user': {
                    'type': 'user',
                    'id': str(user.uuid)
                }
            }
        }
        data = format_jsonapi_request('order', order)
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))
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
        user = add_user('12345@email.com', TEST_USER_PSW)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')
        order = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 4},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf034r3',
                     'type': 'item', 'quantity': 10}
                ],
                'delivery_address': {
                    'type': 'address',
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8'
                },
                'user': {
                    'type': 'user',
                    'id': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
                }
            }
        }
        path = 'orders/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(order))
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_update_order__new_item(self):

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=15
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=15
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order1 = Order.create(
            delivery_address=addr,
            user=user
        ).add_item(item1, 2)

        order = {
            "relationships": {
                'items': [{
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    'type': 'item', 'quantity': 5,
                     }, {
                    'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                    'type': 'item', 'quantity': 10,
                }]
            }
        }
        post_data = format_jsonapi_request('order', order)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))
        order = Order.get()
        expected_result = EXPECTED_RESULTS['update_order__new_item']

        assert json.loads(resp.data) == expected_result

    def test_update_order__item_quantity_zero(self):
        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2,
        )
        item2 = Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=2
        )

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr = add_address(user=user)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order = Order.create(
            delivery_address=addr,
            user=user
        ).add_item(item1, 2).add_item(item2)

        post_data = {
            "relationships": {
                    'items': [{
                        'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                        'type': 'item', 'quantity': 0,
                    }]
            }
        }
        post_data = format_jsonapi_request('order', post_data)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))
        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['update_order__item_quantity_zero']

        assert json.loads(resp.data) == expected_result

        # test remove with quantity=0 functionality, item1 is not present.
        assert len(order.order_items) == 1
        assert order.order_items[0].item == item2

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
        addr = add_address(user=user, id='86ba7e70-b3c0-4c9c-8d26-a14f49360e47')
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        order = Order.create(
            delivery_address=addr,
            user=user,
        ).add_item(item1, 10).add_item(item2, 20)

        post_data = {
            "relationships": {
                    'items': [{
                        'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                        'type': 'item', 'quantity': 0,
                    }],
                    'delivery_address': {
                        'type': 'address',
                        'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    }
            }
        }
        post_data = format_jsonapi_request('order', post_data)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))
        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['update_order__remove_item_without_delete']

        assert json.loads(resp.data) == expected_result
        assert len(order.order_items) == 1
        assert order.order_items[0].quantity == 20

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

        order = Order.create(delivery_address=addr_A, user=user)
        order.add_item(item1, 5).add_item(item2, 20)

        post_data = {
            "relationships": {
                    'items': [{
                        'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                        'type': 'item', 'quantity': 10,
                    }]
            }
        }
        post_data = format_jsonapi_request('order', post_data)

        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))
        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['update_order__add_item']

        assert json.loads(resp.data) == expected_result

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

        user = add_user('12345@email.com', TEST_USER_PSW,
                        id='90c3e1c1-b51c-4224-b69d-17f84f6a8dfc')
        addr = add_address(
            user=user, id='8f3b518e-9c17-4103-9a47-b274740726e7')
        add_address(
            user=user, id='284ac7f6-40c2-4da6-b722-5d8cd248b1cc')
        order = Order.create(
            delivery_address=addr,
            user=user,
            uuid='9d899e2d-66e8-4728-aee5-fee733807b4a'
        ).add_item(item1, 2).add_item(item2)

        post_data = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 5},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 1}
                ],
                'delivery_address': {
                    'type': 'address',
                    'id': '284ac7f6-40c2-4da6-b722-5d8cd248b1cc'
                },
                'user': {
                    'type': 'user',
                    'id': '90c3e1c1-b51c-4224-b69d-17f84f6a8dfc'
                }
            }
        }
        post_data = format_jsonapi_request('order', post_data)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))

        expected_result = EXPECTED_RESULTS['update_order__success']

        assert resp.status_code == OK
        assert json.loads(resp.data) == expected_result

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
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf00000',
                     'type': 'item', 'quantity': 1},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf2222',
                     'type': 'item', 'quantity': 1},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf9999',
                     'type': 'item', 'quantity': 2}
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

        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)

        order1 = Order.create(
            delivery_address=addr_A, user=user
        ).add_item(item1, 2).add_item(item2)
        order_item_before = order1.order_items

        order = {
            "order": {
                'items': [
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf00000',
                     'type': 'item', 'quantity': 1},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf2222',
                     'type': 'item', 'quantity': 1},
                ],
                'delivery_address': '577ad826-a79d-41e9-a5b2-7955bcf5423',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(order))

        assert resp.status_code == BAD_REQUEST
        assert order_item_before == order1.order_items

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

        user = add_user('12345@email.com', TEST_USER_PSW,
                        id='35b9d92a-83c4-48c6-bc2a-580d95951f99')
        addr_A = add_address(
            user=user, id='7f7bc402-469c-4f7b-8918-d4e150469ac7')

        order1 = Order.create(
            delivery_address=addr_A,
            user=user,
            uuid='54a2b917-6c21-42b5-b273-39ad6c765187'
        ).add_item(item1, 2).add_item(item2)

        order = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 5},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 1}
                ],
            }
        }
        data = format_jsonapi_request('order', order)

        user_B = add_admin_user('admin_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user_B.email, TEST_USER_PSW, 'application/json',
                              json.dumps(data))

        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['update_order__success_admin_not_owner']
        assert json.loads(resp.data) == expected_result

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
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 5},
                ],
            }
        }
        data = format_jsonapi_request('order', order)

        path = 'orders/{}'.format(order_uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(data))

        assert resp.status_code == NOT_FOUND

    def test_update_order__failure_availability(self, mocker):
        mocker.patch('views.orders.database', new=self.TEST_DB)

        user = add_user('12345@email.com', TEST_USER_PSW,
                        id='90c3e1c1-b51c-4224-b69d-17f84f6a8dfc')
        addr = add_address(
            user=user, id='8f3b518e-9c17-4103-9a47-b274740726e7')
        item = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=4
        )
        order = Order.create(
            delivery_address=addr,
            user=user,
        ).add_item(item, 2)

        update_order = {
            'relationships': {
                'items': [{
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                    'type': 'item', 'quantity': 5
                }]
            }
        }
        post_data = format_jsonapi_request('order', update_order)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              '12345@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))

        assert resp.status_code == BAD_REQUEST
        assert OrderItem.select().count() == 1
        assert OrderItem.get() == order.order_items[0]
        assert order.order_items[0].quantity == 2

    def test_update_order__failure_non_existing_empty_orders(self):
        user = add_user('user@email.com', TEST_USER_PSW)
        add_address(user=user, id='429994bf-784e-47cc-a823-e0c394b823e8')

        uuid = str(uuid4())

        order = {
            "order": {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 5},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 1}
                ],
                'delivery_address': '429994bf-784e-47cc-a823-e0c394b823e8',
                'user': '86ba7e70-b3c0-4c9c-8d26-a14f49360e47'
            }
        }
        data = format_jsonapi_request('order', order)
        path = '/orders/{}'.format(uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              'user@email.com', TEST_USER_PSW, 'application/json',
                              json.dumps(data))

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
            user=user
        ).add_item(item1, 2).add_item(item2)

        post_data = {
            'relationships': {
                'items': [
                    {'id': '429994bf-784e-47cc-a823-e0c394b823e8',
                     'type': 'item', 'quantity': 5},
                    {'id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
                     'type': 'item', 'quantity': 1}
                ],
                'delivery_address': {
                    'type': 'address',
                    'id': '429994bf-784e-47cc-a823-e0c394b823e8'
                },
                'user': {
                    'type': 'user',
                    'id': '90c3e1c1-b51c-4224-b69d-17f84f6a8dfc'
                }
            }
        }
        post_data = format_jsonapi_request('order', post_data)
        user_B = add_user('wrong_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'PATCH',
                              user_B.email, TEST_USER_PSW, 'application/json',
                              json.dumps(post_data))

        assert resp.status_code == UNAUTHORIZED

    def test_delete_order__success(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)
        addr_B = add_address(user=user)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address=addr_B, user=user)

        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              '12345@email.com', TEST_USER_PSW, None,
                              None)

        assert resp.status_code == NO_CONTENT
        assert len(Order.select()) == 1
        assert len(OrderItem.select()) == 0
        assert Order.get(uuid=order2.uuid)

    def test_delete_order__success_admin_not_own_order(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)
        addr_B = add_address(user=user)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user)
        order1.add_item(item1, 2)

        order2 = Order.create(delivery_address=addr_B, user=user)

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
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)

        item1 = Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=2
        )
        order1 = Order.create(delivery_address=addr_A, user=user)
        order1.add_item(item1, 2)

        user_B = add_user('admin_user@email.com', TEST_USER_PSW)
        path = 'orders/{}'.format(order1.uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_B.email, TEST_USER_PSW, None,
                              None)

        assert resp.status_code == UNAUTHORIZED

    def test_delete_order__failure_non_existing_empty_orders(self):
        user = add_user('12345@email.com', TEST_USER_PSW)

        path = 'orders/{}'.format(str(uuid4()))
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user.email, TEST_USER_PSW, None,
                              None)
        assert resp.status_code == NOT_FOUND

    def test_delete_order__failure__failure_non_existing(self):
        user = add_user('12345@email.com', TEST_USER_PSW)
        addr_A = add_address(user=user)
        Order.create(delivery_address=addr_A, user=user)

        resp = self.app.delete('/orders/{}'.format(uuid4()))

        path = 'orders/{}'.format(str(uuid4()))
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user.email, TEST_USER_PSW, None,
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
            name='Item 2',
            description='Item 2 description',
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
