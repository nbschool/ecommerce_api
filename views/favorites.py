from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite, Item
from utils import check_required_fields, to_json
from http.client import (CREATED, NOT_FOUND, OK, BAD_REQUEST)
import uuid


class FavoritesHandler(Resource):
    """TEST DOCSTRING"""
    @auth.login_required
    def get(self):
        user = g.user
        favorites = user.favorites
        result = []
        for favorite in favorites:
            result.append(favorite.json())
        return result, OK

    @auth.login_required
    def post(self):
        user = g.user
        item_uuid = request.json[0]['item_uuid']
        check_required_fields(
            request_data=request.get_json(),
            required_fields=('item_uuid', 'user_uuid'),
        )

        item = Item.select().where(Item.uuid == item_uuid).get()
        has_already = Item.is_favorite(self, user, item)

        if has_already:
            return { "message" : "ALREADY_INSERTED" }.json() , OK

        favorite = Favorite.create(
                uuid=uuid.uuid4(),
                item=item,
                user=user,
        )
        return favorite.json(), CREATED
