"""
Test suite for ItemHandler and ItemListHandler
"""

import json
import os
import uuid

import http.client as client

from models import Item, Picture
from tests.test_case import TestCase
from tests import test_utils
import utils

TEST_IMAGE_FOLDER = 'test_images'

TEST_ITEM = {
    'uuid': '429994bf-784e-47cc-a823-e0c394b823e8',
    'name': 'mario',
    'price': 20.20,
    'description': 'svariati mariii',
    'availability': 1,
}
TEST_ITEM2 = {
    'uuid': '577ad826-a79d-41e9-a5b2-7955bcf03499',
    'name': 'GINO',
    'price': 30.20,
    'description': 'svariati GINIIIII',
    'availability': 2,
}
TEST_ITEM_WRONG = {
    'uuid': '19b4c6dc-e393-4e76-bf0f-72559dd5d32e',
    'name': '',
    'price': 30.20,
    'description': 'svariati GINIIIII',
    'availability': 3,
}
TEST_ITEM_PRECISION = {
    'uuid': '68e587f7-3982-4b6a-a882-dd43b89134fe',
    'name': 'Anna Pannocchia',
    'price': 30.222222,
    'description': 'lorem ipsum',
    'availability': 1,
}
TEST_ITEM_AVAILABILITY = {
    'uuid': '68e587f7-3982-4b6a-a882-dd43b89134fe',
    'name': 'Anna Pannocchia',
    'price': 30.00,
    'description': 'lorem ipsum',
    'availability': -1,
}
TEST_PICTURE = {
    'uuid': 'df690434-a488-419f-899e-8853cba1a22b',
    'extension': 'jpg'
}

TEST_PICTURE2 = {
    'uuid': 'c0001a48-10a3-43c1-b87b-eabac0b2d42f',
    'extension': 'png'
}

TEST_PICTURE3 = {
    'uuid': 'c489bd0f-1e7a-4aaa-ba9b-4145bbb87160',
    'extension': 'png'
}

WRONG_UUID = '04f2f213-1a0f-443d-a5ab-79097ba725ba'


class TestItems(TestCase):

    @classmethod
    def setup_class(cls):
        super(TestItems, cls).setup_class()
        utils.get_image_folder = lambda: TEST_IMAGE_FOLDER
        test_utils.get_image_folder = utils.get_image_folder

    def test_post_item__success(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM),
                             content_type='application/json')
        assert resp.status_code == client.CREATED
        assert len(Item.select()) == 1
        item = Item.select()[0].json()
        assert item['name'] == TEST_ITEM['name']
        assert item['price'] == TEST_ITEM['price']
        assert item['description'] == TEST_ITEM['description']
        assert item['availability'] == TEST_ITEM['availability']
        try:
            uuid.UUID(item['uuid'], version=4)
        except ValueError:
            assert False

    def test_post_item__not_json_failure(self):
        resp = self.app.post('/items/', data=test_utils.wrong_dump(TEST_ITEM),
                             content_type='application/json')
        assert resp.status_code == client.BAD_REQUEST
        assert len(Item.select()) == 0

    def test_post_item__failed(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM_WRONG),
                             content_type='application/json')
        assert resp.status_code == client.BAD_REQUEST

    def test_post_item__round_price(self):
        resp = self.app.post('/items/', data=json.dumps(TEST_ITEM_PRECISION),
                             content_type='application/json')
        assert resp.status_code == client.CREATED
        item = Item.select().get()
        assert round(TEST_ITEM_PRECISION['price'], 5) == float(item.price)
        assert not TEST_ITEM_PRECISION['price'] == item.price
        assert TEST_ITEM_PRECISION['name'] == item.name
        assert TEST_ITEM_PRECISION['description'] == item.description
        assert TEST_ITEM_PRECISION['availability'] == item.availability

    def test_post_item__availability(self):
        resp = self.app.post('/items/',
                             data=json.dumps(TEST_ITEM_AVAILABILITY),
                             content_type='application/json')
        assert resp.status_code == client.BAD_REQUEST
        assert not Item.select().exists()

    def test_get_items__success(self):
        Item.create(**TEST_ITEM)
        Item.create(**TEST_ITEM2)
        resp = self.app.get('/items/')
        items = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(items) == 2
        assert TEST_ITEM in items
        assert TEST_ITEM2 in items

    def test_get_item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.get('/items/{item_uuid}'.format(item_uuid=item.uuid))
        assert resp.status_code == client.OK
        assert json.loads(resp.data) == TEST_ITEM

    def test_get_item__failed(self):
        resp = self.app.get('/items/{item_uuid}'.format(item_uuid=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_patch_change1item__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.patch('/items/{item_uuid}'.format(item_uuid=item.uuid),
                              data=json.dumps({'name': 'new-name'}),
                              content_type='application/json')
        assert resp.status_code == client.OK
        json_item = Item.get(Item.uuid == item.uuid).json()
        assert json_item['name'] == 'new-name'
        assert json_item['price'] == TEST_ITEM['price']
        assert json_item['description'] == TEST_ITEM['description']
        assert json_item['availability'] == TEST_ITEM['availability']
        assert json_item['uuid'] == item.uuid
        assert json.loads(resp.data) == json_item

    def test_patch_allitems_success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.patch('/items/{item_uuid}'.format(item_uuid=item.uuid),
                              data=json.dumps(
                                  {'name': 'new-name', 'price': 40.20,
                                   'description': 'new-description',
                                   'availability': 2}),
                              content_type='application/json')
        assert resp.status_code == client.OK
        json_item = Item.get(Item.uuid == item.uuid).json()
        assert json_item['name'] == 'new-name'
        assert json_item['price'] == 40.20
        assert json_item['description'] == 'new-description'
        assert json_item['availability'] == 2
        assert json_item['uuid'] == item.uuid
        assert json.loads(resp.data) == json_item

    def test_patch_item__wrong_uuid(self):
        Item.create(**TEST_ITEM)
        resp = self.app.patch('/items/{item_uuid}'.format(item_uuid=WRONG_UUID),
                              data=json.dumps(TEST_ITEM2),
                              content_type='application/json')
        assert resp.status_code == client.NOT_FOUND

    def test_patch_item__failed(self):
        resp = self.app.patch('/items/{item_uuid}'.format(item_uuid=WRONG_UUID),
                              data=json.dumps(TEST_ITEM),
                              content_type='application/json')
        assert resp.status_code == client.NOT_FOUND

    def test_delete_item__success(self):
        item = Item.create(**TEST_ITEM2)
        resp = self.app.delete('/items/{item_uuid}'.format(item_uuid=item.uuid))
        assert resp.status_code == client.NO_CONTENT
        assert not Item.select().exists()

    def test_delete_item__pictures_cascade(self):
        """
        delete a selected item and all its binded pictures
        """
        test_utils.setup_images()
        item = Item.create(**TEST_ITEM)
        item2 = Item.create(**TEST_ITEM2)
        picture = Picture.create(item=item, **TEST_PICTURE)
        picture2 = Picture.create(item=item, **TEST_PICTURE2)
        picture3 = Picture.create(item=item2, **TEST_PICTURE3)
        path_pic = os.path.join(utils.get_image_folder(), "{picture_uuid}.{extension}".format(
            picture_uuid=picture.uuid,
            extension=picture.extension))
        path_pic2 = os.path.join(utils.get_image_folder(), "{picture_uuid}.{extension}".format(
            picture_uuid=picture2.uuid,
            extension=picture2.extension))
        path_pic3 = os.path.join(utils.get_image_folder(), "{picture_uuid}.{extension}".format(
            picture_uuid=picture3.uuid,
            extension=picture3.extension))
        open(path_pic, "wb")
        open(path_pic2, "wb")
        open(path_pic3, "wb")

        resp = self.app.delete('/items/{item_uuid}'.format(
            item_uuid=item.uuid))

        assert resp.status_code == client.NO_CONTENT
        assert Picture.select().count() == 1
        assert Item.select().count() == 1
        item2 = Item.get()
        pic = Picture.get()
        assert pic == picture3
        assert os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture3.uuid,
            extension=picture3.extension))
        assert not os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture.uuid,
            extension=picture.extension))
        assert not os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture2.uuid,
            extension=picture2.extension))
        test_utils.clean_images()

    def test_delete_item__failed(self):
        resp = self.app.delete('/items/{item_uuid}'.format(item_uuid=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND
