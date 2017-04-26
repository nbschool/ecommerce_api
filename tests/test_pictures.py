"""
Test suite for PictureHandler, ItemPictureHandler and PicturesHandler
"""

import json
from io import BytesIO
import os
import uuid

import http.client as client

from models import Item, Picture
from tests.test_case import TestCase
from tests.test_utils import clean_images, setup_images
import utils

TEST_IMAGE_FOLDER = 'test_images'

TEST_ITEM = {
    'item_id': '429994bf-784e-47cc-a823-e0c394b823e8',
    'name': 'mario',
    'price': 20.20,
    'description': 'svariati mariii'
}

TEST_ITEM2 = {
    'item_id': 'd46b13a1-f4bb-4cfb-8076-6953358145f3',
    'name': 'GINO',
    'price': 30.20,
    'description': 'svariati GINIIIII'
}

TEST_PICTURE = {
    'picture_id': 'df690434-a488-419f-899e-8853cba1a22b',
    'extension': 'jpg'
}

TEST_PICTURE2 = {
    'picture_id': 'c0001a48-10a3-43c1-b87b-eabac0b2d42f',
    'extension': 'png'
}

WRONG_UUID = 'e8e42371-46de-4f5e-8927-e2cc34826269'


class TestPictures(TestCase):

    @classmethod
    def setup_class(cls):
        super(TestPictures, cls).setup_class()
        utils.get_image_folder = lambda: TEST_IMAGE_FOLDER

    def test_get_picture__success(self):
        setup_images()
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        open("{path}/{picture_id}.jpg".format(
            path=utils.get_image_folder(),
            picture_id=picture.picture_id), "wb")
        resp = self.app.get('/pictures/{picture_id}'.format(
            picture_id=picture.picture_id))
        assert resp.status_code == client.OK

        test_picture = TEST_PICTURE.copy()
        test_picture['item_id'] = item.item_id
        assert resp.data == b''
        assert resp.headers['Content-Type'] == 'image/jpeg'
        clean_images()

    def test_get_picture__missing(self):
        resp = self.app.get('/pictures/{picture_id}'.format(
            picture_id=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_get_pictures__success(self):
        item = Item.create(**TEST_ITEM)
        item2 = Item.create(**TEST_ITEM2)
        Picture.create(item=item, **TEST_PICTURE)
        Picture.create(item=item2, **TEST_PICTURE2)
        resp = self.app.get('/pictures/')
        pictures = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(pictures) == 2

        test_picture = TEST_PICTURE.copy()
        test_picture['item_id'] = item.item_id
        test_picture2 = TEST_PICTURE2.copy()
        test_picture2['item_id'] = item2.item_id
        assert test_picture in pictures
        assert test_picture2 in pictures

    def test_get_pictures__empty(self):
        resp = self.app.get('/pictures/')
        pictures = json.loads(resp.data)
        assert not len(pictures)

    def test_get_item_pictures__success(self):
        item = Item.create(**TEST_ITEM)
        Picture.create(item=item, **TEST_PICTURE)
        Picture.create(item=item, **TEST_PICTURE2)
        resp = self.app.get('/items/{item_id}/pictures/'.format(
            item_id=item.item_id))
        pictures = json.loads(resp.data)
        assert resp.status_code == client.OK
        assert len(pictures) == 2

        test_picture = test_picture2 = TEST_PICTURE.copy()
        test_picture['item_id'] = test_picture2['item_id'] = item.item_id
        assert test_picture in pictures
        assert test_picture2 in pictures

    def test_get_item_pictures__empty(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.get('/items/{item_id}/pictures/'.format(
            item_id=item.item_id))
        pictures = json.loads(resp.data)
        assert not len(pictures)

    def test_get_item_pictures__wrong_item_id(self):
        resp = self.app.get('/items/{item_id}/pictures/'.format(
            item_id=WRONG_UUID))
        assert resp.status_code == client.NOT_FOUND

    def test_post_picture__success(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_id}/pictures/'.format(
            item_id=item.item_id),
            data={'image': (BytesIO(b'my file contents'), 'testimage.jpg')},
            content_type='multipart/form-data')
        assert resp.status_code == client.CREATED
        assert len(Picture.select()) == 1
        picture = Picture.get()
        assert picture.item == item
        assert picture.extension == 'jpg'
        assert type(picture.picture_id) == uuid.UUID

    def test_post_item_pictures__wrong_item_id(self):
        resp = self.app.post('/items/{item_id}/pictures/'.format(
            item_id=WRONG_UUID),
            data={'image': (BytesIO(b'my file contents'), 'testimage.jpg')},
            content_type='multipart/form-data')
        assert resp.status_code == client.NOT_FOUND
        assert Picture.select().count() == 0

    def test_post_item_pictures__wrong_extension(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_id}/pictures/'.format(
            item_id=item.item_id),
            data={'image': (BytesIO(b'my file contents'), 'testimage.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == client.BAD_REQUEST
        assert Picture.select().count() == 0

    def test_post_picture__no_image(self):
        item = Item.create(**TEST_ITEM)
        resp = self.app.post('/items/{item_id}/pictures/'.format(
            item_id=item.item_id),
            data={},
            content_type='multipart/form-data')
        assert resp.status_code == client.BAD_REQUEST
        assert Picture.select().count() == 0

    def test_delete_picture__success(self):
        setup_images()
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        picture2 = Picture.create(item=item, **TEST_PICTURE2)
        open("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=picture.picture_id,
            extension=picture.extension), "wb")
        open("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=WRONG_UUID,
            extension='jpg'), "wb")
        open("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=picture2.picture_id,
            extension=picture2.extension), "wb")

        resp = self.app.delete('/pictures/{picture_id}'.format(
            picture_id=picture.picture_id))

        assert resp.status_code == client.NO_CONTENT
        assert Picture.select().count() == 1
        assert Item.select().count() == 1
        item2 = Item.get()
        assert str(item2.item_id) == TEST_ITEM['item_id']
        assert item2.name == TEST_ITEM['name']
        assert float(item2.price) == TEST_ITEM['price']
        assert item2.description == TEST_ITEM['description']
        assert os.path.isfile("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=WRONG_UUID,
            extension='jpg'))
        assert not os.path.isfile("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=picture.picture_id,
            extension=picture.extension))
        assert os.path.isfile("{path}/{picture_id}.{extension}".format(
            path=utils.get_image_folder(),
            picture_id=picture2.picture_id,
            extension=picture2.extension))
        clean_images()

    def test_delete_picture__wrong_id(self):
        resp = self.app.delete('/pictures/{picture_id}'.format(
            picture_id=WRONG_UUID))

        assert resp.status_code == client.NOT_FOUND

    def test_delete_pictures__missing_file(self):
        item = Item.create(**TEST_ITEM)
        picture = Picture.create(item=item, **TEST_PICTURE)
        resp = self.app.delete('/pictures/{picture_id}'.format(
            picture_id=picture.picture_id))

        assert resp.status_code == client.NO_CONTENT
        assert not Picture.select().exists()
        assert Item.select().exists()
        assert item.json() == TEST_ITEM
