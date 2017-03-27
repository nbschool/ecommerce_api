from flask_restful import Resource
from ..models import api

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"


class PictureListHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        pass

    def post(self):
        """Insert a new item"""
        pass


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


api.add_resource(PictureListHandler, "/pictures/")
api.add_resource(PictureHandler, "/pictures/<int:picture_id>")
