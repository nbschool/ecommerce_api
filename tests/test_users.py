"""
Test suite for User(s) resources.
"""

from models import User, Address, Item, Order
from tests.test_utils import open_with_auth, add_user, add_address, wrong_dump
from tests.test_case import TestCase
from http.client import (OK, NOT_FOUND, NO_CONTENT, BAD_REQUEST,
                         CREATED, CONFLICT, UNAUTHORIZED)
import json
import uuid

# main endpoint for API
API_ENDPOINT = '/{}'
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'


class TestUser(TestCase):
    """
    Implements py.test suite for User Resource endpoints.
    """

    def test_get_empty_list__success(self):
        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == []
        assert User.select().count() == 0

    def test_get_users_list__success(self):
        user1 = add_user(None, TEST_USER_PSW)
        user2 = add_user(None, TEST_USER_PSW)

        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == [user1.json(), user2.json()]
        assert User.select().count() == 2

    def test_post_new_user__success(self):
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg',
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == CREATED

        resp_user = json.loads(resp.data)

        assert 'user_id' in resp_user

        del user['password']  # user inside response does not have the password
        del resp_user['user_id']  # sent user data does not have the id field
        assert resp_user == user
        assert User.select().count() == 1
        for user in User.select():
            assert user.admin is False

    def test_post_new_user__not_json_failure(self):
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg',
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=wrong_dump(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_post_new_user_email_exists__fail(self):
        add_user('mail@gmail.com', TEST_USER_PSW)
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mail@gmail.com',
            'password': 'aksdg',
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == CONFLICT
        assert json.loads(resp.data)['message'] == 'email already present.'
        assert User.select().count() == 1

    def test_post_new_user_no_email__fail(self):
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'password': 'aksdg',
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_post_new_user_empty_str_field__fail(self):
        user = {
            'first_name': '',
            'last_name': 'Rossi',
            'email': 'mario@email.com',
            'password': 'akjsgdf',
        }

        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_delete_user__success(self):
        # TODO: refactor for auth implementation
        email = 'mail@email.it'
        user = add_user(email, TEST_USER_PSW)

        user_path = 'users/{}'.format(user.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              email, TEST_USER_PSW, None, None)
        assert resp.status_code == NO_CONTENT
        assert User.select().count() == 0

    def test_delete_user__cascade(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=1,
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1,
        )
        email = 'mail@email.it'
        user = add_user(email, TEST_USER_PSW)
        user1 = add_user('mail2@hotmail.com', TEST_USER_PSW)
        addr = add_address(user=user)
        addr1 = add_address(user=user1)
        Order.create(delivery_address=addr, user=user)
        order1 = Order.create(delivery_address=addr1, user=user1)

        user_path = 'users/{}'.format(user.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              email, TEST_USER_PSW, None, None)
        assert resp.status_code == NO_CONTENT
        assert Address.select().count() == 1
        assert Order.select().count() == 1
        assert User.select().count() == 1
        addr2 = Address.get()
        assert addr2 == addr1
        order2 = Order.get()
        assert order2 == order1
        user2 = User.get()
        assert user2 == user1

    def test_delete_user_dont_exists__fail(self):
        user = add_user(None, TEST_USER_PSW)

        wrong_uuid = uuid.UUID(int=user.user_id.int + 1)
        user_path = 'users/{}'.format(wrong_uuid)

        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == NOT_FOUND
        assert User.select().count() == 1

    def test_delete_user_other_user__fail(self):
        user_A = add_user('user.a@users.com', TEST_USER_PSW)
        user_B = add_user('user.b@users.com', TEST_USER_PSW)

        path = 'users/{}'.format(user_A.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_B.user_id, TEST_USER_PSW, None, None)

        assert resp.status_code == UNAUTHORIZED
        assert User.get(User.email == user_A.email)
        assert User.exists(user_A.email)
        assert User.select().count() == 2

    def test_delete_user_auth_does_not_exists__fail(self):
        user = add_user(None, TEST_USER_PSW)

        path = 'users/{}'.format(user.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              'donot@exists.com', 'unused_psw', None, None)

        assert resp.status_code == UNAUTHORIZED
        assert User.exists(user.email)
