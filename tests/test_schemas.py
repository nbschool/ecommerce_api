"""
Testing module for Marshmallow-JSONApi implementation on Peewee Models.
Tests run with no flask involvment and are used to check validation
of inputs (post/put request data) and output from the Schemas dump method, that
will be used as return value for Flask-Restful endpoint handlers.
"""

from models import User
from schemas import UserSchema
from uuid import uuid4
from tests.test_case import TestCase

USER_TEST_DICT = {
    "first_name": "Monty",
    "last_name": "Python",
    "email": "montsdf@asdhon.org",
    "password": "ewrwer"
}


def get_expected_serialized_user(user):
    """
    From USER_TEST_DICT and a generated User, get a dict that should match
    the return value of the JSONApi serialization for that user.
    TODO: Implement expected orders/data serialization if user has orders.
    """

    user_data = USER_TEST_DICT.copy()
    del user_data['password']
    return {
        'data': {
            'type': 'user',
            'id': str(user.user_id),
            'attributes': user_data,
            'links': {
                'self': '/users/{}'.format(user.user_id)
            },
            'relationships': {
                'orders': {
                    'data': []
                }
            },
        },
        'links': {
            'self': '/users/{}'.format(user.user_id)
        }
    }


class TestUserSchema(TestCase):
    def test_user_json__success(self):
        user = User(**USER_TEST_DICT, user_id=uuid4())
        parsed_user, errors = UserSchema.jsonapi(user)

        expected_result = get_expected_serialized_user(user)

        assert parsed_user == expected_result

    def test_user_validate_input__success(self):
        # Simulate what should come from the http POST request
        post_data = {
            'data': {
                'type': 'user',
                'attributes': USER_TEST_DICT
            }
        }
        valid_user, errors = UserSchema.validate_input(post_data)

        assert valid_user is True
        assert errors == {}

    def test_user_validate_input_missing_attributes__fail(self):
        wrong_user_data = USER_TEST_DICT.copy()
        # password field is required on input
        del wrong_user_data['password']
        # Simulate what should come from the http POST request
        post_data = {
            'data': {
                'type': 'user',
                'attributes': wrong_user_data
            }
        }

        validated, errors = UserSchema.validate_input(post_data)

        assert validated is not True
        assert errors == {'errors': [{
            'detail': 'Missing data for required field.',
            'source': {'pointer': '/data/attributes/password'}
        }]}
