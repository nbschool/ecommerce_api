# test json method
# test get class Schema
# test request input validation
# test jsonAPI schema output

from peewee import SqliteDatabase
from models import User
from schemas import UserSchema
from marshmallow_jsonschema import JSONSchema

from marshmallow import pprint
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



class TestUserSchema:
    @classmethod
    def setup_class(cls):
        User._meta.database = TEST_DB
        User.create_table()

    def setup_method(self, test_method):
        User.delete().execute()

    def test_user_json__success(self):
        user = User(**USER_TEST_DICT)
        parsed_user = UserSchema.json(user)

        # expected serialized dict must hide the password field
        expected_result = USER_TEST_DICT.copy()
        del expected_result['password']

        assert parsed_user == expected_result

    def test_user_json__fail(self):
        expected_result = USER_TEST_DICT.copy()
        del expected_result['password']

        assert expected_result != USER_TEST_DICT
        assert 'password' not in expected_result

    def test_user_json_schema__success(self):
        user_schema = JSONSchema().dump(UserSchema()).data
        expected_result = USER_SCHEMA

        assert user_schema == expected_result

    def test_user_validate_input__success(self):
        parsed_user = UserSchema.validate_input(USER_TEST_DICT)

        assert parsed_user == True

    def test_user_validate_input__fail(self):
        expected_result = USER_TEST_DICT.copy()
        del expected_result['password']

        parsed_user = UserSchema.validate_input(expected_result)

        assert parsed_user is not True
        assert 'password' in parsed_user
        assert parsed_user['password'] == ['Missing data for required field.']
