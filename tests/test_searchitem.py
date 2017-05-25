from tests.test_case import TestCase

import http.client as client
import os

import simplejson as json

import utils

from models import Item, Picture
from tests import test_utils
from tests.test_utils import format_jsonapi_request, RESULTS, assert_valid_response

class TestSearchItems(TestCase):

    @classmethod
    def setup_class(cls):
        super(TestSearchItems, cls).setup_class()
        utils.get_image_folder = lambda: TEST_IMAGE_FOLDER
        test_utils.get_image_folder = utils.get_image_folder

    def test_get_search__success(self):
        import pdb; pdb.set_trace()
        data = "sedia"
        resp = self.app.get('/items/db/', data=json.dumps(data),
                             content_type='application/json')
        assert resp.status_code == client.OK
    