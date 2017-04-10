import json
import uuid

from peewee import SqliteDatabase
import http.client as client

from app import app
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Item, Address, User
from tests.test_utils import add_user, open_with_auth

TEST_USER_PSW = '123'


def get_test_addr_dict(user, country='Italy', city='Pistoia', post_code='51100',
                       address='Via Verdi 12', phone='3294882773'):
    return {
        'address_id': uuid.uuid4(),
        'user': user,
        'user_first_name': user.first_name,
        'user_last_name': user.last_name,
        'country': country,
        'city': city,
        'post_code': post_code,
        'address': address,
        'phone': phone
    }


class TestAddresses:
    @classmethod
    def setup_class(cls):
        test_db = SqliteDatabase(':memory:')
        Address._meta.database = test_db
        User._meta.database = test_db
        test_db.connect()
        Address.create_table()
        User.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Address.delete().execute()
        User.delete().execute()

    def test_get_addresses__empty(self):

        user = add_user('mariorossi@gmail.com', TEST_USER_PSW)

        resp = open_with_auth(self.app, '/addresses/', 'GET', user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_addresses__success(self):

        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user))
        user1 = add_user('giovanniverdi@gmail.com', '456')
        addr1 = Address.create(**get_test_addr_dict(user))

        resp = open_with_auth(self.app, '/addresses/', 'GET', user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == [addr.json(), addr1.json()]