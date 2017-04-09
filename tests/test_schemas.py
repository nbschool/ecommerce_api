"""
Testing module for Marshmallow-JSONApi implementation on Peewee Models.
Tests run with no flask involvment and are used to check validation
of inputs (post/put request data) and output from the Schemas dump method, that
will be used as return value for Flask-Restful endpoint handlers.

TODO:
* test json method
* test get class Schema
* test request input validation
* test jsonAPI schema output
"""

from peewee import SqliteDatabase
from models import User
from schemas import UserSchema
from uuid import uuid4
# tests are run in temp database in memory
TEST_DB = SqliteDatabase(':memory:')

# dictionary containing a test user data
USER_TEST_DICT = {
    "first_name": "Monty",
    "last_name": "Python",
    "email": "montsdf@asdhon.org",
    "password": "ewrwer"
}

USER_SCHEMA = {
    'properties': {
        'email': {'title': 'email', 'type': 'string'},
        'first_name': {'title': 'first_name', 'type': 'string'},
        'last_name': {'title': 'last_name', 'type': 'string'},
        'password': {'title': 'password', 'type': 'string'}
    },
    'required': ['email', 'first_name', 'last_name', 'password'],
    'type': 'object'
}


def get_expected_serialized_user(user):
    """
    From USER_TEST_DICT and a generated User, get a dict that should match
    the return value of the JSONApi serialization for that user.
    """

    user_data = USER_TEST_DICT.copy()
    del user_data['password']
    return {
        'data': {
            'type': 'user',
            'id': str(user.user_id),
            'attributes': user_data
        }
    }


class TestUserSchema:
    @classmethod
    def setup_class(cls):
        User._meta.database = TEST_DB
        User.create_table()

    def setup_method(self, test_method):
        User.delete().execute()

    def test_user_json__success(self):
        user = User(**USER_TEST_DICT, user_id=uuid4())
        parsed_user, errors = UserSchema.json(user)

        expected_result = get_expected_serialized_user(user)

        assert parsed_user == expected_result

    def test_user_json__fail(self):
        # FIXME: What does this test do?
        assert False

        expected_result = USER_TEST_DICT.copy()
        del expected_result['password']

        assert expected_result != USER_TEST_DICT
        assert 'password' not in expected_result

    def test_user_json_schema__success(self):
        assert UserSchema.json_schema() == USER_SCHEMA

    def test_user_validate_input__success(self):
        valid_user = UserSchema.validate_input(USER_TEST_DICT)

        assert valid_user is True

    def test_user_validate_input__fail(self):
        wrong_user_data = USER_TEST_DICT.copy()
        # password field is required on input
        del wrong_user_data['password']

        validated = UserSchema.validate_input(wrong_user_data)

        assert validated is not True
        assert 'password' in validated
        assert validated['password'] == ['Missing data for required field.']
