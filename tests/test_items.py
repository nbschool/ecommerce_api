"""
Test suite for ItemHandler and ItemListHandler
"""

import json

from peewee import SqliteDatabase
import http.client as client

from app import app
from models import Item

TEST_ITEM = {
    'name': 'mario',
    'price': 20.20,
    'description': 'svariati mariii'
}
TEST_ITEM2 = {
    'name': 'GINO',
    'price': 30.20,
    'description': 'svariati GINIIIII'
}
TEST_ITEM_WRONG = {
    'name': '',
    'price': 30.20,
    'description': 'svariati GINIIIII'
}
TEST_ITEM_PRECISION = {
    'name': 'Anna Pannocchia',
    'price': 30.222222,
    'description': 'lorem ipsum'
}


class TestItems:
    @classmethod
    def setup_class(cls):
        Item._meta.database = SqliteDatabase(':memory:')
        Item.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()

    def test_post_item__success(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM),
                             content_type='application/json')
        assert resp.status_code == client.CREATED
        assert len(Item.select()) == 1
        assert Item.select()[0].json() == TEST_ITEM

    def test_post_item__failed(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM_WRONG),
                             content_type='application/json')
        assert resp.status_code == client.BAD_REQUEST

    def test_post_item__round_price(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM_PRECISION),
                             content_type='application/json')
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
        resp = self.app.get('/items/{item_id}'.format(item_id=item.id))
        assert resp.status_code == client.OK
        assert json.loads(resp.data) == TEST_ITEM

    def test_get_item__failed(self):
        resp = self.app.get('/items/{item_id}'.format(item_id=1))
        assert resp.status_code == client.NOT_FOUND

    def test_put_item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.put('/items/{item_id}'.format(item_id=item.id),
                            data=json.dumps(TEST_ITEM2),
                            content_type='application/json')
        assert resp.status_code == client.OK
        db_item = Item.select().where(Item.id == item.id).get()
        assert db_item.json() == TEST_ITEM2

    def test_put_item__failed(self):
        resp = self.app.put('/items/{item_id}'.format(item_id=1),
                            data=json.dumps(TEST_ITEM),
                            content_type='application/json')
        assert resp.status_code == client.NOT_FOUND

    def test_delete_item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.delete('/items/{item_id}'.format(item_id=item.id))
        assert resp.status_code == client.NO_CONTENT
        assert not Item.select().exists()

    def test_delete_item__failed(self):
        resp = self.app.delete('/items/{item_id}'.format(item_id=1))
        assert resp.status_code == client.NOT_FOUND
