import json
import uuid

from peewee import SqliteDatabase
import http.client as client

from app import app
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address, User
from tests.test_utils import add_user, open_with_auth
from uuid import uuid4

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


def new_addr(user, country='Italy', city='Pistoia', post_code='51100',
             address='Via Verdi 12', phone='3294882773'):
    return {
        'user_id': str(user.user_id),
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
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                              post_code='50132', address="Via Rossi 10"))
        addr1 = Address.create(**get_test_addr_dict(user))

        resp = open_with_auth(self.app, '/addresses/', 'GET', user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == OK
        assert json.loads(resp.data) == [addr.json(), addr1.json()]

    def test_create_address__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == CREATED
        assert len(Address.select()) == 1
        assert str(Address.get().user.user_id) == addr['user_id']
        address = Address.get().json()
        assert address['country'] == addr['country']
        assert address['city'] == addr['city']
        assert address['address'] == addr['address']
        assert address['phone'] == addr['phone']

    def test_create_address__failure_missing_field(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)
        del addr['country']

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_create_address__failure_empty_field(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)
        addr['country'] = ""

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_get_address(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                              post_code='50132', address="Via Rossi 10"))
        Address.create(**get_test_addr_dict(user))

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.address_id), 'GET',
                              user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == addr.json()

    def test_get_address__failed(self):
        user = add_user('mariorossi@gmail.com', '123')
        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'GET',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NOT_FOUND
