import json
from uuid import uuid4

from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address
from tests.test_case import TestCase
from tests.test_utils import add_user, open_with_auth, wrong_dump

TEST_USER_PSW = '123'


def get_test_addr_dict(user, country='Italy', city='Pistoia', post_code='51100',
                       address='Via Verdi 12', phone='3294882773'):
    return {
        'address_id': uuid4(),
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


class TestAddresses(TestCase):

    def test_create_address__not_json_failure(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              wrong_dump(addr))

        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_get_addresses__empty(self):
        user = add_user('mariorossi@gmail.com', TEST_USER_PSW)

        resp = open_with_auth(self.app, '/addresses/',
                              'GET', user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_addresses__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                                                   post_code='50132', address="Via Rossi 10"))
        addr1 = Address.create(**get_test_addr_dict(user))

        resp = open_with_auth(self.app, '/addresses/',
                              'GET', user.email, TEST_USER_PSW, None, None)
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

    def test_patch_only_city__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                                                   post_code='50132', address="Via Rossi 10"))

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.address_id), 'PATCH',
                              user.email, TEST_USER_PSW, data=json.dumps(
                                  {'city': "Genova"}),
                              content_type='application/json')
        assert resp.status_code == OK
        address = Address.get(Address.address_id == addr.address_id).json()
        assert address['country'] == addr.country
        assert address['city'] == 'Genova'
        assert address['address'] == addr.address
        assert address['phone'] == addr.phone
        assert address['post_code'] == addr.post_code
        assert json.loads(resp.data) == address

    def test_patch_all__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                                                   post_code='50132', address="Via Rossi 10"))

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.address_id), 'PATCH',
                              user.email, TEST_USER_PSW, data=json.dumps(
                                  {"country": "Germany", "city": "Genova",
                                   "address": "Via XX Settembre, 30", "phone": "01050675",
                                   "post_code": "16100"}),
                              content_type='application/json')
        assert resp.status_code == OK
        address = Address.get(Address.address_id == addr.address_id).json()
        assert address['country'] == "Germany"
        assert address['city'] == "Genova"
        assert address['address'] == "Via XX Settembre, 30"
        assert address['phone'] == "01050675"
        assert address['post_code'] == "16100"
        assert json.loads(resp.data) == address

    def test_patch_address__wrong_id(self):
        user = add_user('mariorossi@gmail.com', '123')
        Address.create(**get_test_addr_dict(user, city="Firenze",
                                            post_code='50132', address="Via Rossi 10"))
        addr1 = new_addr(user, city="Roma", post_code="10000",
                         address="Via Bianchi 20")

        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'PATCH',
                              user.email, TEST_USER_PSW, data=json.dumps(
                                  addr1),
                              content_type='application/json')
        assert resp.status_code == NOT_FOUND

    def test_delete_address__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = Address.create(**get_test_addr_dict(user, city="Firenze",
                                                   post_code='50132', address="Via Rossi 10"))

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.address_id), 'DELETE',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NO_CONTENT
        assert not Address.select().exists()

    def test_delete_address__failed(self):
        user = add_user('mariorossi@gmail.com', '123')
        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'DELETE',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NOT_FOUND
