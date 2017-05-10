from tests.test_utils import add_user, open_with_auth
from tests.test_case import TestCase
from models import Favorite
from http.client import OK, NOT_FOUND, UNAUTHORIZED

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

    def test_get_favorites_pass__wrong(self):
        user = add_user(USER1, PASS1)
        user_path = 'favorites/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                      user.email, PASS2, None, None)
        assert resp.status_code == UNAUTHORIZED
