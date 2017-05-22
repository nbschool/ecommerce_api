from auth import auth
from flask import g, request
from flask_restful import Resource
from models import Favorite, Item, Address
from utils import check_required_fields
from http.client import (CREATED, NOT_FOUND, OK)
from utils import generate_response


class FavoritesHandler(Resource):
    @auth.login_required
    def get(self):
        user = g.user
        # favorites = user.favorites
        # result = []
        # for favorite in favorites:
        #     result.append(favorite.json())
        # data = Favorite.json_list(user.favorites)
        
        # return generate_response(data, OK)
        # return result, OK
        data = Favorite.json_list(Favorite.select())
        return generate_response(data, OK)

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

        favorite = user.add_favorite(item)

        # return favorite.json(), CREATED
        return generate_response(favorite.json(), CREATED)


class FavoriteHandler(Resource):
    @auth.login_required
    def delete(self, favorite_uuid):
        try:
            favorite = Favorite.get(Favorite.user_id == g.user.id)
        except Favorite.DoesNotExist:
            return {'message': 'item `{}` not found'.format(favorite_uuid)}, NOT_FOUND

        if favorite.user_id == g.user.id:
            g.user.delete_favorite()
            return {'message': 'item `{}` deleted'.format(favorite_uuid)}, OK
