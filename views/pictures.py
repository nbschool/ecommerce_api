from flask_restful import Resource
from ..models import api

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"


class PictureListHandler(Resource):
    """Handler of the collection of pictures"""

    def get(self):
        """Retrieve every picture"""
        pass

    def post(self):
        """Insert a new picture"""
        pass


class PictureHandler(Resource):
    """Handler of a specific picture"""

    def get(self, picture_id):
        """Retrieve the picture specified by picture_id"""
        pass

    def delete(self, picture_id):
        """Remove the picture specified by picture_id"""
        pass


api.add_resource(PictureListHandler, "/pictures/")
api.add_resource(PictureHandler, "/pictures/<int:picture_id>")
