from tests.test_utils import RESULTS, add_user, open_with_auth, add_favorite, add_item, assert_valid_response
from tests.test_case import TestCase
from http.client import OK, UNAUTHORIZED, CREATED, NOT_FOUND
import json

USER1 = 'fatima.caputo@tiscali.it'
USER2 = 'pepito.pepon@gmail.com'
PASS1 = '9J0'
PASS2 = '0J9'
# main endpoint for API
API_ENDPOINT = '/{}'
EXPECTED_RESULTS = RESULTS['favorites']


class TestFavorites(TestCase):

    def test_get_favorites__empty(self):
        user = add_user(USER1, PASS1)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS1, None, None)
        assert resp.status_code == OK
        assert json.loads(resp.data) == []

    def test_get_favorites__success(self):
        user = add_user(USER1, PASS1)
        item = add_item()
        favorite = add_favorite(user, item)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS1, None, None)
        assert resp.status_code == OK
        expected_result = EXPECTED_RESULTS['get_favorites__success']
        assert_valid_response(resp.data, expected_result)

    def test_get_favorites2__success(self):
        user = add_user(USER1, PASS1)
        user2 = add_user(USER2, PASS2)
        item = add_item()
        item2 = add_item()
        item3 = add_item()
        favorite = add_favorite(user, item)
        favorite2 = add_favorite(user2, item2)
        favorite3 = add_favorite(user, item3)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS1, None, None)
        assert resp.status_code == OK
        expected_result = EXPECTED_RESULTS['get_favorites2__success']
        assert_valid_response(resp.data, expected_result)

    def test_get_favorites_pass__wrong(self):
        user = add_user(USER1, PASS1)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS2, None, None)
        assert resp.status_code == UNAUTHORIZED

    def test_get_favorites_pass2__wrong(self):
        """Forced case where a users uses the password of another user."""
        user1 = add_user(USER1, PASS1)
        user2 = add_user(None, PASS2)  # noqa: F841
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user1.email, PASS2, None, None)
        assert resp.status_code == UNAUTHORIZED

    def test_get_favorites_pass3__wrong(self):
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              None, None, None, None)
        assert resp.status_code == UNAUTHORIZED
        assert resp.get_data() == b'Unauthorized Access'

    def test_post_favorites__fail(self):
        user = add_user(USER1, PASS1)
        data = {"item_uuid": "3", "user_uuid": str(user.uuid)}
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'POST',
                              user.email, PASS1, 'application/json',
                              json.dumps(data))
        assert resp.status_code == OK
        assert resp.data == b'{"message": "Item 3 doesn\'t exist."}\n'

    def test_post_favorites_success(self):
        user = add_user(USER1, PASS1)
        item = add_item()
        data = {"item_uuid": str(item.uuid),
                "user_uuid": str(user.uuid),
                }
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'POST',
                              user.email, PASS1, 'application/json',
                              json.dumps(data))
        # import pdb; pdb.set_trace()
        assert resp.status_code == CREATED
        expected_result = EXPECTED_RESULTS['post_favorites__success']
        assert_valid_response(resp.data, expected_result)


    def test_delete_favorites__success(self):
        user = add_user(USER1, PASS1)
        item = add_item()
        add_favorite(user, item)
        user_path = 'favorites/{}'.format(str(item.uuid))
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              user.email, PASS1, None, None)

        assert resp.status_code == OK
        assert len(resp.data) == 67

    def test_delete_favorites__fail(self):
        user = add_user(USER1, PASS1)
        item = add_item()
        add_favorite(user, item)
        user_path = 'favorites/{}'.format(str(item.uuid))
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              user.email, PASS2, None, None)

        assert resp.status_code == UNAUTHORIZED

    def test_delete_alien_favorites__fail(self):
        user1 = add_user(USER1, PASS1)
        user2 = add_user(USER2, PASS2)
        item = add_item()
        add_favorite(user2, item)
        user_path = 'favorites/{}'.format(str(item.uuid))
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              user1.email, PASS1, None, None)

        assert resp.status_code == NOT_FOUND
