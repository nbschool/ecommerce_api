from flask import request 
from flask_restful import Resource
from models import Favorite
from http.client import (CREATED, NO_CONTENT, NOT_FOUND, OK,
                         BAD_REQUEST, CONFLICT, UNAUTHORIZED)
import uuid

class FavoritesHandler(Resource):
    """TEST DOCSTRING"""
    def get():
        favorites = [f.json() for f in Favorite.select()]

        if favorites:
            return favorites, OK
        return None, NOT_FOUND