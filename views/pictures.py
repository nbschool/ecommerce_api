import os
import uuid

from models import Picture

from flask_restful import Resource, reqparse
import http.client as client
import werkzeug

IMAGE_FOLDER = 'images'
ALLOWED_EXTENSION = ['.jpg', '.jpeg', '.png', '.gif']


class PicturesHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        pass

    def post(self):
        """Insert a new picture"""
        parser = reqparse.RequestParser()
        parser.add_argument('image', location='files',
                            type=werkzeug.datastructures.FileStorage)
        args = parser.parse_args(strict=True)
        image = self._save_image(args['image'])
        if not image:
            return {"message": "File extension not allowed"},\
                client.BAD_REQUEST
        return image.json(), client.CREATED

    def _save_image(self, file):
        extension = os.path.splitext(file.filename)[1]
        if extension not in ALLOWED_EXTENSION:
            return None
        filename = str(uuid.uuid4()) + extension
        full_path = os.path.join(IMAGE_FOLDER, filename)
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
        file.save(full_path)
        return Picture(image=full_path)


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
