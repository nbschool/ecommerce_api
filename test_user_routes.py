"""
Test suite for flask restful api endpoints for users.
"""

from user_routes import app
from models.user import User
from peewee import SqliteDatabase
from http.client import OK
import json
import uuid
import random

# main endpoint for API
API_ENDPOINT = '/api/{}'
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')


# TODO: Utility functions:
#   - check_length(<int>) to check the table' size

def _add_user():
    """Create a single user in the test database. """
    return User.create(
        first_name='John',
        last_name='Doe',
        email='johndoe{}@email.com'.format(int(random.random() * 100)),
        password='afoihseg',
        objectID=uuid.uuid4()
    )


class Testuser:
    """Implements py.test suite for User operations. """

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
