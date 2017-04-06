"""
Test suite for User(s) resources.
"""

from app import app
from base64 import b64encode
from models import User
from tests.test_utils import open_with_auth, add_user
from peewee import SqliteDatabase
from http.client import (OK, NOT_FOUND, NO_CONTENT, BAD_REQUEST,
                         CREATED, CONFLICT, UNAUTHORIZED)
import json
import random
import uuid

# main endpoint for API
API_ENDPOINT = '/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'




class Testuser:
    """
    Implements py.test suite for User Resource endpoints.
    """

    @classmethod
    def setup_class(cls):
        User._meta.database = TEST_DB
        User.create_table()

        # Setup the Flask test client
        cls.app = app.test_client()

    def setup_method(self, test_method):
        User.delete().execute()

    def test_get_empty_list__success(self):
        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == []
        assert User.select().count() == 0

    def test_get_users_list__success(self):
        user1 = add_user(None, TEST_USER_PSW)
        user2 = add_user(None,TEST_USER_PSW)

        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == [user1.json(), user2.json()]
        assert User.select().count() == 2

    def test_post_new_user__success(self):
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg'
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

    def test_post_new_user_no_json__fail(self):
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg'
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user))

        assert resp.status_code == BAD_REQUEST

    def test_post_new_user_email_exists__fail(self):
        add_user('mail@gmail.com', TEST_USER_PSW)
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mail@gmail.com',
            'password': 'aksdg'
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
            'password': 'aksdg'
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
            'password': 'akjsgdf'
        }

        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_delete_user__success(self):
        # TODO: refactor for auth implementation
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        user_path = 'users/{}'.format(email)
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                                   email, TEST_USER_PSW)
        assert resp.status_code == NO_CONTENT
        assert User.select().count() == 0

    def test_delete_user_dont_exists__fail(self):
        user = add_user(None, TEST_USER_PSW)
        wrong_uuid = uuid.UUID(int=user.user_id.int + 1)
        user_path = 'users/{}'.format(wrong_uuid)
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                                   user.email, TEST_USER_PSW)

        assert resp.status_code == NOT_FOUND
        assert User.select().count() == 1

    def test_delete_user_other_user__fail(self):
        user_A = add_user('user.a@users.com', TEST_USER_PSW)
        user_B = add_user('user.b@users.com', TEST_USER_PSW)

        path = 'users/{}'.format(user_A.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                                   user_B.user_id, TEST_USER_PSW)

        assert resp.status_code == UNAUTHORIZED
        assert User.get(User.email == user_A.email)
        assert User.exists(user_A.email)
        assert User.select().count() == 2

    def test_delete_user_auth_does_not_exists__fail(self):
        user = add_user(None, TEST_USER_PSW)


        path = 'users/{}'.format(user.user_id)
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                                   'donot@exists.com', 'unused_psw')

        assert resp.status_code == UNAUTHORIZED
        assert User.exists(user.email)
