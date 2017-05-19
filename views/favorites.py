from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite, Item
from utils import check_required_fields
from http.client import (CREATED, NOT_FOUND, OK)


class FavoritesHandler(Resource):
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
        item_uuid = request.json['item_uuid']
        check_required_fields(
            request_data=request.get_json(),
            required_fields=('item_uuid', 'user_uuid'),
        )

        try:
            item = Item.select().where(Item.uuid == item_uuid).get()
        except:
            return {"message": "ITEM DOESN'T EXIST"}, OK

        has_already = Item.is_favorite(self, user, item)

        if has_already:
            return {"message": "ALREADY INSERTED"}, OK

        favorite = Favorite.add_favorite(self, item, user)

        return favorite.json(), CREATED


class FavoriteHandler(Resource):
    @auth.login_required
    def delete(self, favorite_uuid):
        user_id = g.user.id

        result = Favorite.remove_favorite(self, favorite_uuid, user_id)
        if result[1] == 'NOT_FOUND':
            return result[0], NOT_FOUND
        if result[1] == 'OK':
            return result[0], OK

        
