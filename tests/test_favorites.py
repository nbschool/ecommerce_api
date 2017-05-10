from tests.test_utils import add_user, open_with_auth
from tests.test_case import TestCase
from models import Favorite
from http.client import OK

USER1 = 'fatima.caputo@tiscali.it'
PASS1 = '9J0'
# main endpoint for API
API_ENDPOINT = '/{}'

class TestFavorites(TestCase):

    def test_get_favorites__empty(self):
        user = add_user(USER1, PASS1)
        user_path = 'favorite/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'GET',
                      USER1, PASS1, None, None)
        assert resp.status_code == OK
        assert json.loads(resp.data) == []