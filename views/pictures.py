import os
import utils
import uuid

from flask import request, send_from_directory
from flask_restful import Resource
import http.client as client

from models import Item
from models import Picture

ALLOWED_EXTENSION = ['jpg', 'jpeg', 'png', 'gif']


class ItemPictureHandler(Resource):

    def get(self, item_uuid):
        """Retrieve every picture of an item"""
        items = [o.json() for o in Picture.select().join(Item).where(
            Item.uuid == item_uuid)]

        if items:
            return items, client.OK
        return None, client.NOT_FOUND

    def post(self, item_uuid):
        """Insert a new picture for the specified item"""
        if 'image' not in request.files:
            return {"message": "No image received"},\
                client.BAD_REQUEST

        try:
            item = Item.get(Item.uuid == item_uuid)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        file = request.files['image']
        picture_uuid = uuid.uuid4()
        extension = os.path.splitext(file.filename)[1][1:]

        if extension not in ALLOWED_EXTENSION:
            return {"message": "File extension not allowed"},\
                client.BAD_REQUEST

        utils.save_image(file, picture_uuid, extension)

        return Picture.create(
            uuid=picture_uuid,
            extension=extension,
            item=item
        ).json(), client.CREATED


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_uuid):
        """Retrieve the picture specified by picture_uuid"""
        try:
            picture = Picture.get(Picture.uuid == picture_uuid)
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND

        return send_from_directory(utils.get_image_folder(),
                                   picture.filename(), as_attachment=True)

    def delete(self, picture_uuid):
        """Remove the picture specified by picture_uuid"""
        try:
            obj = Picture.get(Picture.uuid == picture_uuid)
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
