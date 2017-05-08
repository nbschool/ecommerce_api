from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite
from utils import check_required_fields
from http.client import (CREATED, NOT_FOUND, OK)
import uuid


class FavoritesHandler(Resource):
    """TEST DOCSTRING"""
    @auth.login_required
    def get(self):
        """TODO Set the user status when logged"""
        user = g.user
        favorites = [f.json() for f in Favorite.select().where(Favorite.user == user.get_id())]

        if favorites:
            return favorites, OK
        return None, NOT_FOUND

    @auth.login_required
    def post(self):
        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['item_id', 'user_id']
            )

        fav = Favorite.add_favorite(self, res)

        new_fav = Favorite.create(
            favorite_id=uuid.uuid4(),
            item_id=fav['item_id'],
            user_id=fav['user_id']
            )

        return new_fav.json(), CREATED
