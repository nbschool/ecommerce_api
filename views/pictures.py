import os
import uuid

from models import Picture

from flask import request
from flask_restful import Resource
import http.client as client

IMAGE_FOLDER = 'images'
ALLOWED_EXTENSION = ['jpg', 'jpeg', 'png', 'gif']


class PicturesHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every picture"""
        return [o.json() for o in Picture.select()], client.OK

    def post(self):
        """Insert a new picture"""
        if 'image' not in request.files:
            return {"message": "No image received"},\
                client.BAD_REQUEST
        file = request.files['image']
        picture = self._save_image(file)

        if not picture:
            return {"message": "File extension not allowed"},\
                client.BAD_REQUEST

        return picture.json(), client.CREATED

    def _save_image(self, file):
        extension = os.path.splitext(file.filename)[1][1:]
        if extension not in ALLOWED_EXTENSION:
            return None
        picture_id = uuid.uuid4()
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
        file.save(self.image_fullpath(picture_id, extension))
        picture = Picture.create(
            picture_id=picture_id,
            extension=extension
        )
        return picture

    @staticmethod
    def image_fullpath(picture_id, extension):
        return os.path.join(
            IMAGE_FOLDER,
            '{}.{}'.format(str(picture_id), extension))


class PictureHandler(Resource):
    """Handler of a specific item"""

    def get(self, iid):
        """Retrieve the item specified by iid"""
        pass

    def put(self, iid):
        """Edit the item specified by iid"""
        pass

    def delete(self, iid):
        """Remove the item specified by iid"""
        pass
