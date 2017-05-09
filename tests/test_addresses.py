from tests.test_case import TestCase
import json
from http.client import BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK


from uuid import uuid4

from models import Address
from tests.test_utils import (add_address, add_user, RESULTS,
                              open_with_auth, format_jsonapi_request, wrong_dump)

TEST_USER_PSW = '123'

EXPECTED_RESULTS = RESULTS['addresses']


def new_addr(user, country='Italy', city='Pistoia', post_code='51100',
             address='Via Verdi 12', phone='3294882773'):
    return {
        'user_uuid': str(user.uuid),
        'country': country,
        'city': city,
        'post_code': post_code,
        'address': address,
        'phone': phone,
        'relationships': {
            'user': {'type': 'user', 'id': str(user.uuid)}
        }
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
        addr = format_jsonapi_request('address', new_addr(user))

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == CREATED
        assert len(Address.select()) == 1

        expected_result = EXPECTED_RESULTS['create_address__success']
        assert json.loads(resp.data) == expected_result

    def test_create_address__failure_missing_field(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)
        del addr['country']
        addr = format_jsonapi_request('address', addr)

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0
        expected_result = EXPECTED_RESULTS['create_address__failure_missing_field']
        assert json.loads(resp.data) == expected_result

    def test_create_address__failure_empty_field(self):
        user = add_user('mariorossi@gmail.com', '123')
        addr = new_addr(user)
        addr['country'] = ""
        addr = format_jsonapi_request('address', addr)

        resp = open_with_auth(self.app, '/addresses/', 'POST',
                              user.email, TEST_USER_PSW, 'application/json',
                              json.dumps(addr))

        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0
        expected_result = EXPECTED_RESULTS['create_address__failure_empty_field']
        assert json.loads(resp.data) == expected_result

    def test_get_address(self):
        user = add_user('mariorossi@gmail.com', '123',
                        id='74df5166-db94-4738-8209-69aa733e36d1')
        addr = add_address(user, city='Firenze',
                           post_code='50132', address='Via Rossi 10',
                           id='4dbf5f2b-e164-4967-9a82-022996a17cc9')

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
        addr_id = '943d754e-5826-4d5c-b878-47edc478b789'
        user = add_user('mariorossi@gmail.com', '123',
                        id='943d754e-5826-4d5c-b878-47edc478b789')
        add_address(user, city="Firenze",
                    post_code='50132', address="Via Rossi 10",
                    id=addr_id)
        addr1 = new_addr(user, city="Roma", post_code="10000",
                         address="Via Bianchi 20")

        addr1 = format_jsonapi_request('address', addr1)

        resp = open_with_auth(self.app, '/addresses/{}'.format(addr_id),
                              'PATCH', user.email, TEST_USER_PSW,
                              data=json.dumps(addr1),
                              content_type='application/json')

        assert resp.status_code == OK
        upd_addr = Address.get(Address.uuid == addr_id).json()
        expected_result = EXPECTED_RESULTS['put_address__success']
        # Check that the response data is what is expected and is also
        # the same as what has ben actually saved
        assert json.loads(resp.data) == expected_result == json.loads(upd_addr)

    def test_patch_address__wrong_uuid(self):
        user = add_user('mariorossi@gmail.com', '123')
        add_address(user, city="Firenze", post_code='50132')
        addr1 = new_addr(user, city="Roma", post_code="10000",
                         address="Via Bianchi 20")
        addr1 = format_jsonapi_request('address', addr1)

        resp = open_with_auth(self.app, '/addresses/{}'.format(uuid4()), 'PATCH',
                              user.email, TEST_USER_PSW,
                              data=json.dumps(addr1),
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
