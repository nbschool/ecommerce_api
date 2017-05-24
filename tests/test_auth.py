import json

from http.client import BAD_REQUEST, OK, UNAUTHORIZED

from tests.test_case import TestCase
from tests.test_utils import add_user

AUTH_API_ENDPOINT = '/auth/login/'
TEST_USER_PASSWORD = 'user_password'
TEST_USER_WRONG_PASSWORD = 'wrong_password'


class TestAuth(TestCase):

    def test_post_auth__success(self):
        user = add_user('user@email.com', TEST_USER_PASSWORD)

        data = json.dumps({
            "email": user.email,
            "password": TEST_USER_PASSWORD,
        })

        resp = self.app.post(AUTH_API_ENDPOINT, data=data,
                             content_type='application/json')

        assert resp.status_code == OK

    def test_post_auth__wrong_password(self):
        user = add_user('user@email.com', TEST_USER_PASSWORD)

        data = json.dumps({
            "email": user.email,
            "password": TEST_USER_WRONG_PASSWORD,
        })

        resp = self.app.post(AUTH_API_ENDPOINT, data=data,
                             content_type='application/json')

        assert resp.status_code == UNAUTHORIZED

    def test_post_auth__non_existing_user(self):

        data = json.dumps({
            "email": "user@email.com",
            "password": TEST_USER_PASSWORD,
        })

        resp = self.app.post(AUTH_API_ENDPOINT, data=data,
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
