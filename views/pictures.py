import os
import werkzeug
from flask_restful import Resource, reqparse
from models import Picture
import http.client as client

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"

IMAGE_FOLDER = 'images'


class PictureListHandler(Resource):
    """Handler of the collection of pictures"""

    def get(self):
        """Retrieve every picture"""
        pass

    def post(self):
        """Insert a new picture"""
        import pdb; pdb.set_trace()
        parser = reqparse.RequestParser()
        parser.add_argument('image', location='files',
                            type=werkzeug.datastructures.FileStorage)
        args = parser.parse_args(strict=True)
        image = self._save_image(args['image'])
        return image.json(), client.CREATED

    def _save_image(file):
        filename = werkzeug.secure_filename(file.filename)
        full_path = os.path.join(IMAGE_FOLDER, filename)
        return Picture(image=full_path)


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_id):
        """Retrieve the picture specified by picture_id"""
        pass

    def delete(self, picture_id):
        """Remove the picture specified by picture_id"""
        pass
