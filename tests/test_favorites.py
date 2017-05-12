from tests.test_utils import add_user, open_with_auth, add_favorite, add_item
from tests.test_case import TestCase
# from models import User, Favorite
from http.client import OK, NOT_FOUND, UNAUTHORIZED
import json

USER1 = 'fatima.caputo@tiscali.it'
PASS1 = '9J0'
PASS2 = '0J9'
# main endpoint for API
API_ENDPOINT = '/{}'


class TestFavorites(TestCase):

    def test_get_favorites__empty(self):
        user = add_user(USER1, PASS1)
        user_path = 'favorites/'
        EXPECTED_MSG = b'[{"Message": "Sorry, You haven\'t select any favorite item yet."}]\n'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS1, None, None)
        assert resp.status_code == NOT_FOUND
        assert resp.data == EXPECTED_MSG

    def test_get_favorites__success(self):
        user = add_user(USER1, PASS1)
        item = add_item()
        favorite = add_favorite(user, item)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                              user.email, PASS1, None, None)
        data = json.loads(resp.data)
        assert resp.status_code == OK
        assert data[0]['user_id'] == str(user.id)
        assert data[0]['item_id'] == str(item.id)
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
