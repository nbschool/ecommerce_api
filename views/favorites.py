from auth import auth
from flask import request
from flask_restful import Resource
from models import Favorite, Item, User
from http.client import (CREATED, NOT_FOUND, OK, BAD_REQUEST)
from utils import generate_response


class FavoritesHandler(Resource):
    @auth.login_required
    def get(self):
        data = Favorite.json_list(auth.current_user.favorites)

        return generate_response(data, OK)

    @auth.login_required
    def post(self):
        user = auth.current_user

        res = request.get_json(force=True)
        errors = Favorite.validate_input(res)
        if errors:
            return errors, BAD_REQUEST

        data = res['data']['attributes']

        try:
            item = Item.get(Item.uuid == data['item_uuid'])
        except Item.DoesNotExist:
            return {"message": "Item {} doesn't exist as Favorite.".format(
                    data['item_uuid'])}, NOT_FOUND

        has_already = Item.is_favorite(user, item)
        if has_already:
            return {"message": "Item {} was already been inserted as Favorite.".format(
                    data['item_uuid'])}, OK

        favorite = user.add_favorite(item)

        return generate_response(favorite.json(), CREATED)


class FavoriteHandler(Resource):
    @auth.login_required
    def delete(self, item_id):
        try:
            item = Item.get(Item.uuid == item_id)
        except Item.DoesNotExist:
            return {"message": "Item {} doesn't exist as Favorite.".format(data['item_uuid'])}, NOT_FOUND

        try:
            favorite = Favorite.get(Favorite.item == item)
        except Favorite.DoesNotExist:
            return {'message': 'Item `{}` not found as Favorite'.format(item_id)}, NOT_FOUND

        if favorite.user != auth.current_user:
            return {'message': 'Item `{}` not found as Favorite'.format(item_id)}, NOT_FOUND

        User.delete_favorite(favorite)
