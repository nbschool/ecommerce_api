import os
import uuid

from models import Picture
import utils

from flask import request
from flask_restful import Resource
import http.client as client

ALLOWED_EXTENSION = ['jpg', 'jpeg', 'png', 'gif']


class PicturesHandler(Resource):
    """Handler of the collection of pictures"""

    def get(self):
        """Retrieve every picture"""
        return [o.json() for o in Picture.select()], client.OK

    def post(self):
        """Insert a new picture"""
        if 'image' not in request.files:
            return {"message": "No image received"},\
                client.BAD_REQUEST

        file = request.files['image']
        picture_id = uuid.uuid4()
        extension = os.path.splitext(file.filename)[1][1:]

        if extension not in ALLOWED_EXTENSION:
            return {"message": "File extension not allowed"},\
                client.BAD_REQUEST

        utils.save_image(file, picture_id, extension)

        return Picture.create(
            picture_id=picture_id,
            extension=extension
        ).json(), client.CREATED


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_id):
        """Retrieve the picture specified by picture_id"""
        try:
            return Picture.get(Picture.picture_id == picture_id).json(),\
                client.OK
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND

    def delete(self, picture_id):
        """Remove the picture specified by picture_id"""
        try:
            obj = Picture.get(Picture.picture_id == picture_id)
        except Picture.DoesNotExist:
            return None, client.NOT_FOUND
        try:
            utils.remove_image(obj.picture_id, obj.extension)
        except OSError:
            # TODO log inconsistency
            return None, client.INTERNAL_SERVER_ERROR
        obj.delete_instance(recursive=True)
        return None, client.NO_CONTENT
