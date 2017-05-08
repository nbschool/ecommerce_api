from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite
from utils import check_required_fields
from http.client import (CREATED, NO_CONTENT, NOT_FOUND, OK,
                         BAD_REQUEST, CONFLICT, UNAUTHORIZED)
import uuid


class FavoritesHandler(Resource):
    """TEST DOCSTRING"""
    @auth.login_required
    def get(self):
        """TODO Set the user status when logged"""
        user = g.user
        favorites = [f.json() for f in Favorite.select()]

        if favorites:
            return favorites, OK
        return None, NOT_FOUND


    @auth.login_required    
    def post(self):
        user = g.user
        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['favorite_id', 'item_id', 'user_id']
            )

        fav = Favorite.create(
            favorite_id=uuid.uuid4(),
            item_id= res[item_id],
            user_id= user
            )

        return fav.json(), CREATED
