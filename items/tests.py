from api import app
from model import Item as ItemModel
from peewee import SqliteDatabase
from http.client import CREATED
from model import connect, close
import json

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
        assert resp.status_code == CREATED
        assert len(ItemModel.select()) == 1

    def test_get_item__success(self):
        item = ItemModel.create(**TEST_ITEM)
        resp = self.app.get('/items/{iid}'.format(iid=item.id))
        assert resp.status_code == OK
        assert json.loads(resp.data) == TEST_ITEM

    def test_put_item__success(self):
        item = ItemModel.create(**TEST_ITEM)
        resp = self.app.put('/items/{iid}'.format(iid=item.id),
                            data=TEST_ITEM2)
        assert resp.status_code == OK
        db_item = ItemModel.select().where(ItemModel.id == item.id).get()
        assert db_item.json() == TEST_ITEM2

