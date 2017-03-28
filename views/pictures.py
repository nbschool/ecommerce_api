import os
import werkzeug
from flask_restful import Resource, reqparse
from models import Picture
import http.client as client
import uuid
__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"

IMAGE_FOLDER = 'images'
ALLOWED_EXTENSION = ['.jpg', '.jpeg', '.png', '.gif']


class PictureListHandler(Resource):
    """Handler of the collection of pictures"""

    def get(self):
        """Retrieve every picture"""
        pass

    def post(self):
        """Insert a new picture"""
        parser = reqparse.RequestParser()
        parser.add_argument('image', location='files',
                            type=werkzeug.datastructures.FileStorage)
        args = parser.parse_args(strict=True)
        image = self._save_image(args['image'])
        if not image:
            return {"message": "File extension not allowed"}, client.BAD_REQUEST
        return image.json(), client.CREATED

    def _save_image(self, file):
        extension = os.path.splitext(file.filename)[1]
        if not extension in ALLOWED_EXTENSION:
            return None
        filename = str(uuid.uuid4()) + extension
        full_path = os.path.join(IMAGE_FOLDER, filename)
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
        file.save(full_path)
        return Picture(image=full_path)


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_id):
        """Retrieve the picture specified by picture_id"""
        pass

    def delete(self, picture_id):
        """Remove the picture specified by picture_id"""
        pass
