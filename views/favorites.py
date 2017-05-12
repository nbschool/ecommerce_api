from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite
from utils import check_required_fields, to_json
from http.client import (CREATED, NOT_FOUND, OK, BAD_REQUEST)
import uuid


class FavoritesHandler(Resource):
    """TEST DOCSTRING"""
    @auth.login_required
    def get(self):
        """TODO Set the user status when logged"""
        user = g.user
        favorites = user.favorites
        message_404 = "Sorry, You haven't select any favorite item yet." 
        if favorites:
            return favorites, OK
        return to_json(message_404), NOT_FOUND

        result = []
        for favorite in user.favorites:
            result.append(favorite.json())
        return result, OK

    @auth.login_required
    def post(self):
        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['item_uuid', 'user_uuid'],
        )

        fav = Favorite.add_favorite(self, res)
        # import pdb; set_trace()
        new_fav = Favorite.create(
            uuid=uuid.uuid4(),
            item_id=fav['item_id'],
            user_id=fav['user_id'],
        )

        return new_fav.json(), CREATED
