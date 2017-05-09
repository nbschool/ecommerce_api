"""
Test suite for PictureHandler and ItemPictureHandler
"""

import json
from io import BytesIO
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
    'uuid': 'd46b13a1-f4bb-4cfb-8076-6953358145f3',
    'name': 'GINO',
    'price': 30.20,
    'description': 'svariati GINIIIII',
    'availability': 1,
}

TEST_PICTURE = {
    'uuid': 'df690434-a488-419f-899e-8853cba1a22b',
    'extension': 'jpg'
}

TEST_PICTURE2 = {
    'uuid': 'c0001a48-10a3-43c1-b87b-eabac0b2d42f',
    'extension': 'png'
}

WRONG_UUID = 'e8e42371-46de-4f5e-8927-e2cc34826269'


class TestPictures(TestCase):

    @classmethod
    def setup_class(cls):
        super(TestPictures, cls).setup_class()
        utils.get_image_folder = lambda: os.path.join(utils.get_project_root(),
                                                      TEST_IMAGE_FOLDER)
        test_utils.get_image_folder = utils.get_image_folder

    def test_get_picture__success(self):
        test_utils.setup_images()
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        open("{path}/{picture_uuid}.jpg".format(
            path=utils.get_image_folder(),
            picture_uuid=picture.uuid), "wb")
        resp = self.app.get('/pictures/{picture_uuid}'.format(
            picture_uuid=picture.uuid))
        assert resp.status_code == client.OK

        test_picture = TEST_PICTURE.copy()
        test_picture['item_uuid'] = item.uuid
        assert resp.data == b''
        assert resp.headers['Content-Type'] == 'image/jpeg'
        test_utils.clean_images()

    def test_get_picture__missing(self):
        resp = self.app.get('/pictures/{picture_uuid}'.format(
            picture_uuid=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_get_item_pictures__success(self):
        item = Item.create(**TEST_ITEM)
        Picture.create(item=item, **TEST_PICTURE)
        Picture.create(item=item, **TEST_PICTURE2)
        resp = self.app.get('/items/{item_uuid}/pictures/'.format(
            item_uuid=item.uuid))
        pictures = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(pictures) == 2

        test_picture = test_picture2 = TEST_PICTURE.copy()
        test_picture['item_uuid'] = test_picture2['item_uuid'] = item.uuid
        assert test_picture in pictures
        assert test_picture2 in pictures

    def test_get_item_pictures__empty(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.get('/items/{item_uuid}/pictures/'.format(
            item_uuid=item.uuid))
        pictures = json.loads(resp.data)
        assert not pictures

    def test_get_item_pictures__wrong_item_uuid(self):
        resp = self.app.get('/items/{item_uuid}/pictures/'.format(
            item_uuid=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_post_picture__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_uuid}/pictures/'.format(
            item_uuid=item.uuid),
            data={'image': (BytesIO(b'my file contents'), 'testimage.jpg')},
            content_type='multipart/form-data')
        assert resp.status_code == client.CREATED
        assert len(Picture.select()) == 1
        picture = Picture.get()
        assert picture.item == item
        assert picture.extension == 'jpg'
        assert type(picture.uuid) == uuid.UUID

    def test_post_item_pictures__wrong_item_uuid(self):
        resp = self.app.post('/items/{item_uuid}/pictures/'.format(
            item_uuid=WRONG_UUID),
            data={'image': (BytesIO(b'my file contents'), 'testimage.jpg')},
            content_type='multipart/form-data')
        assert resp.status_code == client.NOT_FOUND
        assert Picture.select().count() == 0

    def test_post_item_pictures__wrong_extension(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_uuid}/pictures/'.format(
            item_uuid=item.uuid),
            data={'image': (BytesIO(b'my file contents'), 'testimage.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == client.BAD_REQUEST
        assert Picture.select().count() == 0

    def test_post_picture__no_image(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_uuid}/pictures/'.format(
            item_uuid=item.uuid),
            data={},
            content_type='multipart/form-data')
        assert resp.status_code == client.BAD_REQUEST
        assert Picture.select().count() == 0

    def test_delete_picture__success(self):
        test_utils.setup_images()
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        picture2 = Picture.create(item=item, **TEST_PICTURE2)
        open("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture.uuid,
            extension=picture.extension), "wb")
        open("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=WRONG_UUID,
            extension='jpg'), "wb")
        open("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture2.uuid,
            extension=picture2.extension), "wb")

        resp = self.app.delete('/pictures/{picture_uuid}'.format(
            picture_uuid=picture.uuid))

        assert resp.status_code == client.NO_CONTENT
        assert Picture.select().count() == 1
        assert Item.select().count() == 1
        item2 = Item.get()
        assert str(item2.uuid) == TEST_ITEM['uuid']
        assert item2.name == TEST_ITEM['name']
        assert float(item2.price) == TEST_ITEM['price']
        assert item2.description == TEST_ITEM['description']
        assert os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=WRONG_UUID,
            extension='jpg'))
        assert not os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture.uuid,
            extension=picture.extension))
        assert os.path.isfile("{path}/{picture_uuid}.{extension}".format(
            path=utils.get_image_folder(),
            picture_uuid=picture2.uuid,
            extension=picture2.extension))
        test_utils.clean_images()

    def test_delete_picture__wrong_uuid(self):
        resp = self.app.delete('/pictures/{picture_uuid}'.format(
            picture_uuid=WRONG_UUID))

        assert resp.status_code == client.NOT_FOUND

    def test_delete_pictures__missing_file(self):
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        resp = self.app.delete('/pictures/{picture_uuid}'.format(
            picture_uuid=picture.uuid))

        assert resp.status_code == client.NO_CONTENT
        assert not Picture.select().exists()
        assert Item.select().exists()
        assert item.json() == TEST_ITEM
