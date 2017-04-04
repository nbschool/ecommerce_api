"""
Test suite for ItemHandler and ItemListHandler
"""

import json
import uuid

from peewee import SqliteDatabase
import http.client as client

from app import app
from models import Item
from base64 import b64encode

TEST_ITEM = {
    'item_id': '429994bf-784e-47cc-a823-e0c394b823e8',
    'name': 'mario',
    'price': 20.20,
    'description': 'svariati mariii'
}
TEST_ITEM2 = {
    'item_id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
    'name': 'GINO',
    'price': 30.20,
    'description': 'svariati GINIIIII'
}
TEST_ITEM_WRONG = {
    'item_id': '19b4c6dc-e393-4e76-bf0f-72559dd5d32e',
    'name': '',
    'price': 30.20,
    'description': 'svariati GINIIIII'
}
TEST_ITEM_PRECISION = {
    'item_id': '68e587f7-3982-4b6a-a882-dd43b89134fe',
    'name': 'Anna Pannocchia',
    'price': 30.222222,
    'description': 'lorem ipsum'
}
WRONG_UUID = '04f2f213-1a0f-443d-a5ab-79097ba725ba'

# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'


class TestItems:
    @classmethod
    def setup_class(cls):
        Item._meta.database = SqliteDatabase(':memory:')
        Item.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()

    def delete_with_auth(self, url, method, username, password):
        """Generic call to app for http request. """

        AUTH_TYPE = 'Basic'
        bytes_auth = bytes('{}:{}'.format(username, password), 'ascii')
        auth_str = '{} {}'.format(
            AUTH_TYPE, b64encode(bytes_auth).decode('ascii'))

        return self.app.open(url,
                     method=method,
                     headers={'Authorization': auth_str})

    def put_with_auth(self, url, data, content_type, method, username, 
                    password):
        """Generic call to app for http request for PUT request. """

        AUTH_TYPE = 'Basic'
        bytes_auth = bytes('{}:{}'.format(username, password), 'ascii')
        auth_str = '{} {}'.format(
            AUTH_TYPE, b64encode(bytes_auth).decode('ascii'))

        return self.app.put(url,
                     data=data, 
                     content_type=content_type,
                     method=method,
                     headers={'Authorization': auth_str})

    def post_with_auth(self, url, data, content_type, method, username, 
                    password):
        """Generic call to app for http request for POST request. """

        AUTH_TYPE = 'Basic'
        bytes_auth = bytes('{}:{}'.format(username, password), 'ascii')
        auth_str = '{} {}'.format(
            AUTH_TYPE, b64encode(bytes_auth).decode('ascii'))

        return self.app.post(url,
                     data=data, 
                     content_type=content_type,
                     method=method,
                     headers={'Authorization': auth_str})        

    def test_post_item__success(self):
        resp = self.post_with_auth('/items/', data=json.dumps(TEST_ITEM),
                                    content_type='application/json',
                                    method='POST', 
                                    username='test@email.com',
                                    password=TEST_USER_PSW )
        assert resp.status_code == client.CREATED
        assert len(Item.select()) == 1
        item = Item.select()[0].json()
        assert item['name'] == TEST_ITEM['name']
        assert item['price'] == TEST_ITEM['price']
        assert item['description'] == TEST_ITEM['description']
        try:
            uuid.UUID(item['item_id'], version=4)
        except ValueError:
            assert False

    def test_post_item__failed(self):
        resp = self.post_with_auth('/items/', data=json.dumps(TEST_ITEM_WRONG),
                                    content_type='application/json',
                                    method='POST', 
                                    username='test@email.com',
                                    password=TEST_USER_PSW )
        assert resp.status_code == client.BAD_REQUEST

    def test_post_item__round_price(self):
        resp = self.post_with_auth('/items/', data=json.dumps(TEST_ITEM_PRECISION),
                                    content_type='application/json',
                                    method='POST', 
                                    username='test@email.com',
                                    password=TEST_USER_PSW )        
        assert resp.status_code == client.CREATED
        item = Item.select().get()
        assert round(TEST_ITEM_PRECISION['price'], 5) == float(item.price)
        assert not TEST_ITEM_PRECISION['price'] == item.price
        assert TEST_ITEM_PRECISION['name'] == item.name
        assert TEST_ITEM_PRECISION['description'] == item.description

    def test_get_items__success(self):
        Item.create(**TEST_ITEM)
        Item.create(**TEST_ITEM2)
        resp = self.app.get('/items/')
        items = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(items) == 2
        assert TEST_ITEM in items
        assert TEST_ITEM2 in items

    def test_get_item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.get('/items/{item_id}'.format(item_id=item.item_id))
        assert resp.status_code == client.OK
        assert json.loads(resp.data) == TEST_ITEM

    def test_get_item__failed(self):
        resp = self.app.get('/items/{item_id}'.format(item_id=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_put_item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.put_with_auth('/items/{item_id}'.
                                format(item_id=item.item_id), 
                                data=json.dumps(TEST_ITEM2),
                                content_type='application/json',
                                method='PUT', 
                                username='test@email.com',
                                password=TEST_USER_PSW)
        assert resp.status_code == client.OK
        json_item = Item.select().where(
            Item.item_id == item.item_id).get().json()
        assert json_item['name'] == TEST_ITEM2['name']
        assert json_item['price'] == TEST_ITEM2['price']
        assert json_item['description'] == TEST_ITEM2['description']
        assert json_item['item_id'] == item.item_id

    def test_put_item__wrong_id(self):
        Item.create(**TEST_ITEM)
        resp = self.put_with_auth('/items/{item_id}'.
                                format(item_id=WRONG_UUID), 
                                data=json.dumps(TEST_ITEM2),
                                content_type='application/json',
                                method='PUT', 
                                username='test@email.com',
                                password=TEST_USER_PSW)
        assert resp.status_code == client.NOT_FOUND

    def test_put_item__failed(self):
        resp = self.put_with_auth('/items/{item_id}'.
                                format(item_id=WRONG_UUID), 
                                data=json.dumps(TEST_ITEM),
                                content_type='application/json',
                                method='PUT', 
                                username='test@email.com',
                                password=TEST_USER_PSW) 
        assert resp.status_code == client.NOT_FOUND

    def test_delete_item__success(self):
        item = Item.create(**TEST_ITEM2)
        resp = self.delete_with_auth('/items/{item_id}'.
                format(item_id=item.item_id), 'DELETE', 
                'test@email.com', TEST_USER_PSW)
        assert resp.status_code == client.NO_CONTENT
        assert not Item.select().exists()

    def test_delete_item__failed(self):
        resp = self.delete_with_auth('/items/{item_id}'.
                format(item_id=WRONG_UUID), 'DELETE', 
                'test@email.com', TEST_USER_PSW)
        assert resp.status_code == client.NOT_FOUND
