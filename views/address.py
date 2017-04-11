from auth import auth
from flask import abort, g, request
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address, User
from utils import check_required_fields

import uuid


class AddressesHandler(Resource):
    """ Addresses endpoint. """
    @auth.login_required
    def get(self):

        addresses = {}
        user = g.user

        res = (
            Address
            .select()
            .where(Address.user == user)
        )

        return [addr.json() for addr in res], OK

    @auth.login_required
    def post(self):
        user = g.user
        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['country', 'city', 'post_code', 'address', 'phone'])

        addr = Address.create(
            address_id=uuid.uuid4(),
            user=user,
            country=res['country'],
            city=res['city'],
            post_code=res['post_code'],
            address=res['address'],
            phone=res['phone'])

        return addr.json(), CREATED

class AddressHandler(Resource):
    """ Address endpoint. """
