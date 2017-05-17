from tests.test_utils import add_user, open_with_auth, add_favorite, add_item
from tests.test_case import TestCase
from http.client import OK, UNAUTHORIZED, CREATED, NOT_FOUND
import json

USER1 = 'fatima.caputo@tiscali.it'
USER2 = 'pepito.pepon@gmail.com'
PASS1 = '9J0'
PASS2 = '0J9'
# main endpoint for API
API_ENDPOINT = '/{}'


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
        data = json.loads(resp.data)
        assert resp.status_code == OK
        assert data[0]['user_uuid'] == str(user.uuid)
        assert data[0]['item_uuid'] == str(item.uuid)
        assert data[0]['uuid'] == str(favorite.uuid)

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
        """Forced case where a users uses the password of another user."""
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
        assert resp.get_data() == b'{"message": "ITEM DOESN\'T EXIST"}\n'

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
        assert resp.status_code == CREATED
        assert json.loads(resp.get_data())['item_uuid'] == str(item.uuid)
        assert json.loads(resp.get_data())['user_uuid'] == str(user.uuid)
        assert len(json.loads(resp.get_data())['uuid']) == 36
        assert len(json.loads(resp.get_data())) == 3

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
