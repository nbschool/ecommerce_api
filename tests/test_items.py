"""
Test suite for ItemHandler and ItemListHandler
"""

import json

from app import app
from models import Item as ItemModel
from models import connect, close

from peewee import SqliteDatabase
import http.client as client

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"

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


class TestItems:
    @classmethod
    def setup_class(cls):
        ItemModel._meta.database = SqliteDatabase(':memory:')
        connect()
        cls.app = app.test_client()

    @classmethod
    def teardown_class(cls):
        close()

    def setup_method(self):
        ItemModel.delete().execute()

    def test_post_item__success(self):
        resp = self.app.post('/items/', data=TEST_ITEM)
        assert resp.status_code == client.CREATED
        assert len(ItemModel.select()) == 1

    def test_post_item__failed(self):
        resp = self.app.post('/items/', data=TEST_ITEM_WRONG)
        assert resp.status_code == client.BAD_REQUEST

    def test_get_items__success(self):
        ItemModel.create(**TEST_ITEM)
        ItemModel.create(**TEST_ITEM2)
        resp = self.app.get('/items/')
        items = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(items) == 2
        assert TEST_ITEM in items
        assert TEST_ITEM2 in items

    def test_get_item__success(self):
        item = ItemModel.create(**TEST_ITEM)
        resp = self.app.get('/items/{iid}'.format(iid=item.id))
        assert resp.status_code == client.OK
        assert json.loads(resp.data) == TEST_ITEM

    def test_get_item__failed(self):
        resp = self.app.get('/items/{iid}'.format(iid=1))
        assert resp.status_code == client.NOT_FOUND

    def test_put_item__success(self):
        item = ItemModel.create(**TEST_ITEM)
        resp = self.app.put('/items/{iid}'.format(iid=item.id),
                            data=TEST_ITEM2)
        assert resp.status_code == client.OK
        db_item = ItemModel.select().where(ItemModel.id == item.id).get()
        assert db_item.json() == TEST_ITEM2

    def test_put_item__failed(self):
        resp = self.app.put('/items/{iid}'.format(iid=1),
                            data=TEST_ITEM)
        assert resp.status_code == client.NOT_FOUND

    def test_delete_item__success(self):
        item = ItemModel.create(**TEST_ITEM)
        resp = self.app.delete('/items/{iid}'.format(iid=item.id))
        assert resp.status_code == client.NO_CONTENT
        assert not ItemModel.select().exists()

    def test_delete_item__failed(self):
        resp = self.app.delete('/items/{iid}'.format(iid=1))
        assert resp.status_code == client.NOT_FOUND
