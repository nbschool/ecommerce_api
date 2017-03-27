"""
Test suite for User(s) resources.
"""

from app import app
from models import User
from peewee import SqliteDatabase
from http.client import OK, NOT_FOUND, NO_CONTENT, BAD_REQUEST, CREATED
import json
import random

# main endpoint for API
API_ENDPOINT = '/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')


def _add_user(email=None):
    """
    Create a single user in the test database.
    If an email is provided it will be used, otherwise it will be generated
    by the function before adding the User to the database.
    """
    email = email or 'johndoe{}@email.com'.format(int(random.random() * 100))

    return User.create(
        first_name='John',
        last_name='Doe',
        email=email,
        password='afoihseg'
    )


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
        user1 = _add_user()
        user2 = _add_user()

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

        del user['password']
        assert json.loads(resp.data) == user
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
        _add_user('mail@gmail.com')
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mail@gmail.com',
            'password': 'aksdg'
        }
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
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
            'email': 'mario@email.com',
            'last_name': 'Rossi',
            'password': 'akjsgdf',
            'first_name': ''
        }

        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=user,
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_delete_user__success(self):
        email = 'mail@email.it'
        _add_user(email)

        user_path = 'users/{}'.format(email)
        resp = self.app.delete(API_ENDPOINT.format(user_path))

        assert resp.status_code == NO_CONTENT
        assert User.select().count() == 0

    def test_delete_user_no_exists__fail(self):
        email = 'user@email.it'
        _add_user(email)

        user_path = 'users/{}'.format('hi@email.it')
        resp = self.app.delete(API_ENDPOINT.format(user_path))

        assert resp.status_code == NOT_FOUND
        assert User.select().count() == 1
