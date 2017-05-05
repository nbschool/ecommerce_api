import os
import uuid

from models import Item
from models import Picture
import utils

from flask import request, send_from_directory
from flask_restful import Resource
import http.client as client

ALLOWED_EXTENSION = ['jpg', 'jpeg', 'png', 'gif']


class ItemPictureHandler(Resource):

    def get(self, item_id):
        """Retrieve every picture of an item"""
        items = [o.json() for o in Picture.select().join(Item).where(
            Item.item_id == item_id)]

        if items:
            return items, client.OK
        return None, client.NOT_FOUND

    def post(self, item_id):
        """Insert a new picture for the specified item"""
        if 'image' not in request.files:
            return {"message": "No image received"},\
                client.BAD_REQUEST

        try:
            item = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        file = request.files['image']
        picture_id = uuid.uuid4()
        extension = os.path.splitext(file.filename)[1][1:]

        if extension not in ALLOWED_EXTENSION:
            return {"message": "File extension not allowed"},\
                client.BAD_REQUEST

        utils.save_image(file, picture_id, extension)

        return Picture.create(
            picture_id=picture_id,
            extension=extension,
            item=item
        ).json(), client.CREATED


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_id):
        """Retrieve the picture specified by picture_id"""

        try:
            picture = Picture.get(Picture.picture_id == picture_id)
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND

        return send_from_directory(utils.get_image_folder(),
                                   picture.filename(), as_attachment=True)

    def delete(self, picture_id):
        """Remove the picture specified by picture_id"""
        try:
            obj = Picture.get(Picture.picture_id == picture_id)
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
