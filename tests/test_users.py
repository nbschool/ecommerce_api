"""
Test suite for User(s) resources.
"""
import json
from http.client import (BAD_REQUEST, CONFLICT, CREATED, NO_CONTENT,
                         OK, UNAUTHORIZED)

from models import Address, Item, Order, User
from tests.test_case import TestCase
from tests.test_utils import (RESULTS, add_address, add_admin_user, add_user,
                              format_jsonapi_request, open_with_auth,
                              assert_valid_response, wrong_dump)

# main endpoint for API
API_ENDPOINT = '/{}'
# correct password used for all test users.
TEST_USER_PSW = 'my_password123@'

EXPECTED_RESULTS = RESULTS['users']


class TestUser(TestCase):
    """
    Implements py.test suite for User Resource endpoints.
    """

    def test_get_users_list__success(self):
        user = add_admin_user('user@email.com', TEST_USER_PSW)
        add_user('user1@email.com', TEST_USER_PSW,
                 id='4373d5d7-cae5-42bc-b218-d6fc6d18626f')
        add_user('user2@email.com', TEST_USER_PSW,
                 id='9630b105-ca99-4a27-a51d-ab3430bf52d1')

        resp = open_with_auth(self.app, API_ENDPOINT.format('users/'), 'GET',
                              user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK
        expected_result = EXPECTED_RESULTS['get_users_list__success']
        assert_valid_response(resp.data, expected_result)

    def test_post_new_user__success(self):
        user = format_jsonapi_request('user', {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'rossi@email.com',
            'password': 'aksdg',
        })
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == CREATED

        expected_result = EXPECTED_RESULTS['post_new_user__success']
        assert_valid_response(resp.data, expected_result)

        assert User.select().count() == 1
        assert User.get().admin is False

    def test_post_new_user__not_json_failure(self):
        user = format_jsonapi_request('user', {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'asddjkasdjhv',
            'password': 'aksdg',
        })
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=wrong_dump(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_post_new_user_email_exists__fail(self):
        add_user('mail@gmail.com', TEST_USER_PSW)
        user = format_jsonapi_request('user', {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mail@gmail.com',
            'password': 'aksdg',
        })
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == CONFLICT
        assert json.loads(resp.data)['message'] == 'email already present.'
        assert User.select().count() == 1

    def test_post_new_user_no_email__fail(self):
        user = format_jsonapi_request('user', {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'password': 'aksdg',
        })
        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        # TODO: Refactor resource to use the Schema to validate and return
        # errors. response.data should contain the error missing required field
        # email
        assert resp.status_code == BAD_REQUEST
        expected_result = EXPECTED_RESULTS['post_new_user_no_email__fail']
        assert_valid_response(resp.data, expected_result)

        assert User.select().count() == 0

    def test_post_new_user_empty_str_field__fail(self):
        user = format_jsonapi_request('user', {
            'first_name': '',
            'last_name': 'Rossi',
            'email': 'mario@email.com',
            'password': 'akjsgdf',
        })

        resp = self.app.post(API_ENDPOINT.format('users/'),
                             data=json.dumps(user),
                             content_type='application/json')

        assert resp.status_code == BAD_REQUEST
        assert User.select().count() == 0

    def test_patch_change1user_attribute__success(self):
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        post_data = format_jsonapi_request('user', {'first_name': 'new-first-name'})
        content_type = 'application/json'
        user_path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'PATCH',
                              email, TEST_USER_PSW, content_type, json.dumps(post_data))

        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['patch_change1user_attribute__success']
        assert_valid_response(resp.data, expected_result)

        assert User.select().count() == 1
        assert User.get().admin is False
        assert User.get().first_name == 'new-first-name'

    def test_patch_change_all_user_attribute__success(self):
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        post_data = format_jsonapi_request('user', {
            'first_name': 'new-first-name',
            'last_name': 'new-last-name',
            'email': 'new-email@email.it'
        })
        content_type = 'application/json'
        user_path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'PATCH',
                              email, TEST_USER_PSW, content_type, json.dumps(post_data))

        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['patch_change_all_user_attribute__success']
        assert_valid_response(resp.data, expected_result)

        assert User.select().count() == 1
        assert User.get().admin is False
        assert User.get().first_name == 'new-first-name'
        assert User.get().last_name == 'new-last-name'
        assert User.get().email == 'new-email@email.it'

    def test_patch_user_other_user__fail(self):
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        email2 = 'pippo@email.it'

        post_data = format_jsonapi_request('user', {'first_name': 'new-first-name'})
        content_type = 'application/json'
        user_path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'PATCH',
                              email2, TEST_USER_PSW, content_type, json.dumps(post_data))
        assert resp.status_code == UNAUTHORIZED

    def test_get_usersme__success(self):
        email = 'mail@email.it'
        user = add_user(email, TEST_USER_PSW)

        resp = open_with_auth(self.app, API_ENDPOINT.format('users/me/'), 'GET',
                              user.email, TEST_USER_PSW, None, None)

        assert resp.status_code == OK

        expected_result = EXPECTED_RESULTS['get_usersme__success']
        assert_valid_response(resp.data, expected_result)

        assert User.select().count() == 1
        assert User.get().admin is False
        assert User.get().email == email

    def test_get_users_otherme__success(self):
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        email2 = 'pippo@email.it'

        resp = open_with_auth(self.app, API_ENDPOINT.format('users/me/'), 'GET',
                              email2, TEST_USER_PSW, None, None)

        assert resp.status_code == UNAUTHORIZED

    def test_delete_user__success(self):
        email = 'mail@email.it'
        add_user(email, TEST_USER_PSW)

        user_path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path),
                              'DELETE', email, TEST_USER_PSW, None, None)

        assert resp.status_code == NO_CONTENT
        assert User.select().count() == 0

    def test_delete_user__cascade(self):
        Item.create(
            uuid='429994bf-784e-47cc-a823-e0c394b823e8',
            name='mario',
            price=20.20,
            description='svariati mariii',
            availability=1,
            category='scarpe',
        )
        Item.create(
            uuid='577ad826-a79d-41e9-a5b2-7955bcf03499',
            name='GINO',
            price=30.20,
            description='svariati GINIIIII',
            availability=1,
            category='accessori',
        )
        email = 'mail@email.it'
        user = add_user(email, TEST_USER_PSW)
        user1 = add_user('mail2@hotmail.com', TEST_USER_PSW)
        addr = add_address(user=user)
        addr1 = add_address(user=user1)
        Order.create(delivery_address=addr, user=user)
        order1 = Order.create(delivery_address=addr1, user=user1)

        user_path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(user_path), 'DELETE',
                              email, TEST_USER_PSW, None, None)
        assert resp.status_code == NO_CONTENT
        assert Address.select().count() == 1
        assert Order.select().count() == 1
        assert User.select().count() == 1
        addr2 = Address.get()
        assert addr2 == addr1
        order2 = Order.get()
        assert order2 == order1
        user2 = User.get()
        assert user2 == user1

    def test_delete_user_other_user__fail(self):
        user_A = add_user('user.a@users.com', TEST_USER_PSW)
        user_B = add_user('user.b@users.com', TEST_USER_PSW)

        path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              user_B.uuid, TEST_USER_PSW, None, None)

        assert resp.status_code == UNAUTHORIZED
        assert User.get(User.email == user_A.email)
        assert User.exists(user_A.email)
        assert User.select().count() == 2

    def test_delete_user_auth_does_not_exists__fail(self):
        user = add_user(None, TEST_USER_PSW)

        path = 'users/'
        resp = open_with_auth(self.app, API_ENDPOINT.format(path), 'DELETE',
                              'donot@exists.com', 'unused_psw', None, None)

        assert resp.status_code == UNAUTHORIZED
        assert User.exists(user.email)

    def test_get_users_list_not_authenticated__unauthorized(self):
        add_user(None, TEST_USER_PSW)

        resp = self.app.get(API_ENDPOINT.format('users/'))
        assert resp.status_code == UNAUTHORIZED

    def test_get_users_list_authenticated_not_admin__unauthorized(self):
        add_user(None, TEST_USER_PSW)

        user = add_user(None, TEST_USER_PSW)
        resp = open_with_auth(self.app, API_ENDPOINT.format('users/'), 'GET',
                              user.email, TEST_USER_PSW, None, None)

        assert user.admin is False
        assert resp.status_code == UNAUTHORIZED
