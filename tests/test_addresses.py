import json
from http.client import BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK
from uuid import uuid4

from models import Address
from tests.test_case import TestCase
from tests.test_utils import _test_res_patch_id as patch_id
from tests.test_utils import (add_address, add_user, get_expected_results,
                              open_with_auth)

TEST_USER_PSW = '123'

EXPECTED_RESULTS = get_expected_results('addresses')


def new_addr(user, country='Italy', city='Pistoia', post_code='51100',
             address='Via Verdi 12', phone='3294882773'):
    return {
        'user_uuid': str(user.uuid),
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

        resp = open_with_auth(self.app, '/addresses/', 'GET', user.email,
                              TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_addresses__success(self):
        user = add_user('mariorossi@gmail.com', '123',
                        id='9630b105-ca99-4a27-a51d-ab3430bf52d1')
        add_address(user, city="Firenze", post_code='50132',
                    id='f814546c-0dec-45ee-a945-270a7b9cfe2e',
                    address="Via Rossi 10")

        add_address(user, id='943d754e-5826-4d5c-b878-47edc478b789')

        resp = open_with_auth(self.app, '/addresses/', 'GET', user.email,
                              TEST_USER_PSW, None, None)

        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['get_addresses__success']
        assert json.loads(resp.data) == expected_result

    def test_create_address__success(self):
        user = add_user('mariorossi@gmail.com', '123',
                        id='1777e816-3051-4faf-bbba-0c8a87baf08f')
        addr = new_addr(user)

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == CREATED
        assert len(Address.select()) == 1

        expected_result = patch_id(
            EXPECTED_RESULTS['create_address__success'],
            Address.get().address_id)

        assert json.loads(resp.data) == expected_result

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
        user = add_user('mariorossi@gmail.com', '123',
                        id='74df5166-db94-4738-8209-69aa733e36d1')
        addr = add_address(user, city='Firenze',
                           post_code='50132', address='Via Rossi 10',
                           id='4dbf5f2b-e164-4967-9a82-022996a17cc9')
        add_address(user)

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.uuid), 'GET',
                              user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        assert json.loads(resp.data) == EXPECTED_RESULTS['get_address']

    def test_get_address__failed(self):
        user = add_user('mariorossi@gmail.com', '123')
        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'GET',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NOT_FOUND

    def test_put_address__success(self):
        user = add_user('mariorossi@gmail.com', '123',
                        id='943d754e-5826-4d5c-b878-47edc478b789')
        addr = add_address(user, city="Firenze",
                           post_code='50132', address="Via Rossi 10",
                           id='943d754e-5826-4d5c-b878-47edc478b789')
        addr1 = new_addr(user, city="Roma", post_code="10000",
                         address="Via Bianchi 20")

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.uuid), 'PATCH',
                              user.email, TEST_USER_PSW, data=json.dumps(addr1),
                              content_type='application/json')

        assert resp.status_code == OK
        address = Address.get(Address.uuid == addr.uuid).json()
        assert address['country'] == addr.country
        assert address['city'] == 'Genova'
        assert address['address'] == addr.address
        assert address['phone'] == addr.phone
        assert address['post_code'] == addr.post_code
        assert json.loads(resp.data) == address

        expected_result = EXPECTED_RESULTS['put_address__success']
        assert json.loads(resp.data) == expected_result

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.uuid), 'PATCH',
                              user.email, TEST_USER_PSW, data=json.dumps(
                                  {"country": "Germany", "city": "Genova",
                                   "address": "Via XX Settembre, 30", "phone": "01050675",
                                   "post_code": "16100"}),
                              content_type='application/json')
        assert resp.status_code == OK
        address = Address.get(Address.uuid == addr.uuid).json()
        assert address['country'] == "Germany"
        assert address['city'] == "Genova"
        assert address['address'] == "Via XX Settembre, 30"
        assert address['phone'] == "01050675"
        assert address['post_code'] == "16100"
        assert json.loads(resp.data) == address

    def test_patch_address__wrong_uuid(self):
        user = add_user('mariorossi@gmail.com', '123')
        add_address(user, city="Firenze", post_code='50132')
        addr1 = new_addr(user, city="Roma", post_code="10000",
                         address="Via Bianchi 20")

        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'PUT',
                              user.email, TEST_USER_PSW, data=json.dumps(
            addr1),
            content_type='application/json')
        assert resp.status_code == NOT_FOUND

    def test_delete_address__success(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = add_address(user, city="Firenze",
                           post_code='50132', address="Via Rossi 10")

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr.uuid), 'DELETE',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NO_CONTENT
        assert not Address.select().exists()

    def test_delete_address__failed(self):
        user = add_user('mariorossi@gmail.com', '123')
        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'DELETE',
                              user.email, TEST_USER_PSW, None, None)
        assert resp.status_code == NOT_FOUND
