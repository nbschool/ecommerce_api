"""
Test suite for flask restful api endpoints for users.
"""

from app import app
from models import User
from peewee import SqliteDatabase
from http.client import OK
from http.client import CREATED
from http.client import BAD_REQUEST
from http.client import NO_CONTENT
from http.client import NOT_FOUND
import json
import random

# main endpoint for API
API_ENDPOINT = '/api/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')


def _add_user(email=None):
    """
    Create a single user in the test database.
    If an email is provided it will be used, otherwise it will be generated
    by the function before adding the User to the database.
    """
    user_email = 'johndoe{}@email.com'.format(int(random.random() * 100))
    return User.create(
        first_name='John',
        last_name='Doe',
        email=email or user_email,
        password='afoihseg'
    )


class Testuser:
    """Implements py.test suite for User endpoints in Flask-restful app. """

    @classmethod
    def setup_class(cls):
        """Override the default database for testing. """
        User._meta.database = TEST_DB
        User.create_table()

        # Setup the Flask test client
        cls.app = app.test_client()

    def setup_method(self, test_method):
        """Empty the database on every test. """
        User.delete().execute()

    def test_get_empty_list__success(self):
        """Pass if the api returns an empty list of users. """
        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == []
        assert User.select().count() == 0

    def test_get_users_list__success(self):
        """
        Add two users, check that they exists in the database and that
        the API returns a list with all of them.
        """
        user1 = _add_user()
        user2 = _add_user()

        resp = self.app.get(API_ENDPOINT.format('users/'))

        assert resp.status_code == OK
        assert json.loads(resp.data) == [user1.get_json(), user2.get_json()]
        assert User.select().count() == 2

    def test_post_new_user__success(self):
        """Test a correct insert of a new user into the database. """
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg'
        }
        resp = self.app.post(API_ENDPOINT.format('users/'), data=user)

        assert resp.status_code == CREATED

        del user['password']
        assert json.loads(resp.data) == user
        assert User.select().count() == 1

    def test_post_new_user_email_exists__fail(self):
        """Test the case when an existing email is used to signup. """
        _add_user('mail@gmail.com')
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mail@gmail.com',
            'password': 'aksdg'
        }
        resp = self.app.post(API_ENDPOINT.format('users/'), data=user)

        assert resp.status_code == BAD_REQUEST
        assert json.loads(resp.data)['message'] == 'email already present.'
        assert User.select().count() == 1

    def test_post_new_user_no_email__fail(self):
        """Test the case where the email field is missing on the post data. """
        user = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'password': 'aksdg'
        }
        resp = self.app.post(API_ENDPOINT.format('users/'), data=user)

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_post_new_user_empty_str_field__fail(self):
        """Test the case where the name field is missing on the post data. """
        u_data = {
            'email': 'mario@email.com',
            'last_name': 'Rossi',
            'password': 'akjsgdf',
            'first_name': ''
        }

        resp = self.app.post(API_ENDPOINT.format('users/'), data=u_data)

        assert resp.status_code == BAD_REQUEST
        # TODO: find what exception is raised by ReqParse in case of wrong type
        assert User.select().count() == 0

        """Get an user and edit all the fields. """
        pass

    def test_delete_user__success(self):
        """Delete an existing user from the database. """
        email = 'mail@email.email'
        _add_user(email)

        user_path = 'user/{}'.format(email)
        resp = self.app.delete(API_ENDPOINT.format(user_path))
        assert User.select().count() == 0
        assert resp.status_code == NO_CONTENT

    def test_delete_user_no_exists__fail(self):
        """Try to delete an user that does not exists. """
        email = 'user@email.it'
        _add_user(email)
        user_path = 'user/{}'.format('hi@email.it')
        resp = self.app.delete(API_ENDPOINT.format(user_path))
        assert resp.status_code == NOT_FOUND
