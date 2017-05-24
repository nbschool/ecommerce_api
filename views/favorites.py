from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite, Item, User
from http.client import (CREATED, NOT_FOUND, OK, BAD_REQUEST)
from utils import generate_response


class FavoritesHandler(Resource):
    @auth.login_required
    def get(self):
        data = Favorite.json_list(g.user.favorites)

        return generate_response(data, OK)

    @auth.login_required
    def post(self):
        user = g.user

        res = request.get_json(force=True)
        errors = Favorite.validate_input(res)
        if errors:
            return errors, BAD_REQUEST

        data = res['data']['attributes']

        try:
            item = Item.get(Item.uuid == data['item_uuid'])
        except:
            return {"message": "Item {} doesn't exist.".format(data['item_uuid'])}, NOT_FOUND

        has_already = Item.is_favorite(user, item)
        if has_already:
            return {"message": "The item {} was already been inserted.".format(
                    data['item_uuid'])}, OK

        favorite = user.add_favorite(item)

        return generate_response(favorite.json(), CREATED)


class FavoriteHandler(Resource):
    @auth.login_required
    def delete(self, item_id):
        try:
            favorite = Favorite.get(Favorite.user == item_id)
        except Favorite.DoesNotExist:
            return {'message': 'item `{}` not found'.format(item_id)}, NOT_FOUND

        if favorite.user == g.user:
            User.delete_favorite(favorite)
            return {'message': 'item `{}` deleted'.format(favorite.uuid)}, OK
